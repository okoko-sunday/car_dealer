from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from dealers.models import AuditEntry, BuyerRequest, Membership, OutboxEvent, Vehicle
from dealers.services import record_vehicle_change
from .permissions import CanManageInventory, IsDealerStaff
from .serializers import BuyerRequestCreateSerializer, BuyerRequestSerializer, DealerSerializer, VehicleSerializer, VehicleWriteSerializer

def dealer_or_404(request):
    if not getattr(request,"dealer",None):
        from rest_framework.exceptions import NotFound
        raise NotFound("No active dealer matches this hostname.")
    return request.dealer

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    from django.contrib.auth import authenticate
    user=authenticate(request,username=request.data.get("username"),password=request.data.get("password"))
    if not user: return Response({"detail":"Invalid credentials."},status=status.HTTP_400_BAD_REQUEST)
    dealer=dealer_or_404(request)
    membership=Membership.objects.filter(user=user,dealer=dealer,is_active=True).first()
    if not membership: return Response({"detail":"This account cannot access this dealer."},status=status.HTTP_403_FORBIDDEN)
    token,_=Token.objects.get_or_create(user=user)
    return Response({"token":token.key,"user":{"username":user.username,"name":user.get_full_name() or user.username,"role":membership.role},"dealer":DealerSerializer(dealer,context={"request":request}).data})

@api_view(["GET"])
@permission_classes([AllowAny])
def site(request): return Response(DealerSerializer(dealer_or_404(request),context={"request":request}).data)

@api_view(["GET"])
@permission_classes([AllowAny])
def vehicles(request):
    dealer=dealer_or_404(request)
    qs=Vehicle.objects.filter(dealer=dealer,publication_status=Vehicle.Publication.PUBLISHED).prefetch_related("images")
    query=request.query_params.get("q","").strip()
    if query: qs=qs.filter(Q(make__icontains=query)|Q(model__icontains=query)|Q(description__icontains=query))
    if request.query_params.get("make"): qs=qs.filter(make=request.query_params["make"])
    if request.query_params.get("availability"): qs=qs.filter(availability=request.query_params["availability"])
    ordering={"price_low":"price","price_high":"-price","newest":"-published_at"}.get(request.query_params.get("sort"),"-published_at")
    return Response(VehicleSerializer(qs.order_by(ordering),many=True,context={"request":request}).data)

@api_view(["GET","POST"])
@permission_classes([AllowAny])
def vehicle_detail(request,slug):
    vehicle=get_object_or_404(Vehicle.objects.prefetch_related("images"),dealer=dealer_or_404(request),slug=slug,publication_status=Vehicle.Publication.PUBLISHED)
    if request.method=="GET": return Response(VehicleSerializer(vehicle,context={"request":request}).data)
    address=request.META.get("REMOTE_ADDR","unknown"); key=f"api-inquiry:{vehicle.dealer_id}:{address}"
    if cache.get(key,0)>=5: return Response({"detail":"Please wait before sending another request."},status=429)
    if not cache.add(key,1,600): cache.incr(key)
    serializer=BuyerRequestCreateSerializer(data=request.data); serializer.is_valid(raise_exception=True)
    kind=serializer.validated_data["kind"]; serializer.validated_data.pop("consent",None)
    item=serializer.save(dealer=vehicle.dealer,vehicle=vehicle,offer_status=BuyerRequest.OfferStatus.PENDING if kind==BuyerRequest.Kind.OFFER else BuyerRequest.OfferStatus.NOT_APPLICABLE)
    return Response({"id":item.id,"status":"received","next_step":"The dealer will contact you. No booking or sale is confirmed."},status=201)

class StaffOverview(APIView):
    permission_classes=[IsDealerStaff]
    def get(self,request):
        cars=Vehicle.objects.filter(dealer=request.dealer)
        return Response({"dealer":DealerSerializer(request.dealer,context={"request":request}).data,"user":{"name":request.user.get_full_name() or request.user.username,"role":request.membership.role},"counts":{"active":cars.filter(publication_status="published",availability="available").count(),"draft":cars.filter(publication_status="draft").count(),"reserved":cars.filter(availability="reserved").count(),"sold":cars.filter(availability="sold").count()},"vehicles":VehicleSerializer(cars.order_by("-updated_at")[:8],many=True,context={"request":request}).data,"requests":BuyerRequestSerializer(BuyerRequest.objects.filter(dealer=request.dealer).select_related("vehicle").order_by("-created_at")[:8],many=True).data,"outbox":list(OutboxEvent.objects.filter(dealer=request.dealer).order_by("-created_at").values("id","event_type","aggregate_version","status","attempts","last_error","created_at")[:8])})

class StaffVehicles(APIView):
    permission_classes=[IsDealerStaff]
    def get(self,request): return Response(VehicleSerializer(Vehicle.objects.filter(dealer=request.dealer).prefetch_related("images").order_by("-updated_at"),many=True,context={"request":request}).data)
    def post(self,request):
        if request.membership.role not in {Membership.Role.OWNER,Membership.Role.MANAGER}: return Response(status=403)
        serializer=VehicleWriteSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        candidate=Vehicle(dealer=request.dealer,slug="pending",**serializer.validated_data); candidate.slug=slugify(candidate.title)
        if candidate.publication_status==Vehicle.Publication.PUBLISHED: candidate.published_at=timezone.now()
        candidate.save(); record_vehicle_change(candidate,request.user,"vehicle.created")
        return Response(VehicleSerializer(candidate,context={"request":request}).data,status=201)

class StaffVehicleDetail(APIView):
    permission_classes=[CanManageInventory]
    def patch(self,request,pk):
        item=get_object_or_404(Vehicle,pk=pk,dealer=request.dealer); previous=Vehicle.objects.get(pk=pk)
        serializer=VehicleWriteSerializer(item,data=request.data,partial=True); serializer.is_valid(raise_exception=True); item=serializer.save(version=item.version+1)
        if item.publication_status==Vehicle.Publication.PUBLISHED and not item.published_at: item.published_at=timezone.now(); item.save(update_fields=["published_at"])
        record_vehicle_change(item,request.user,"vehicle.updated",previous)
        return Response(VehicleSerializer(item,context={"request":request}).data)

class StaffRequests(APIView):
    permission_classes=[IsDealerStaff]
    def get(self,request): return Response(BuyerRequestSerializer(BuyerRequest.objects.filter(dealer=request.dealer).select_related("vehicle").order_by("-created_at"),many=True).data)
    def patch(self,request,pk):
        if request.membership.role==Membership.Role.VIEWER: return Response(status=403)
        item=get_object_or_404(BuyerRequest,pk=pk,dealer=request.dealer); serializer=BuyerRequestSerializer(item,data=request.data,partial=True); serializer.is_valid(raise_exception=True); item=serializer.save()
        AuditEntry.objects.create(dealer=request.dealer,actor=request.user,entity_type="buyer_request",entity_id=str(item.id),action="buyer_request.updated",data={"status":item.status,"offer_status":item.offer_status})
        return Response(BuyerRequestSerializer(item).data)
