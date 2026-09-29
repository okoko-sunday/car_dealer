from rest_framework.permissions import BasePermission
from dealers.models import Membership

class IsDealerStaff(BasePermission):
    def has_permission(self, request, view):
        dealer = getattr(request,"dealer",None)
        if not request.user.is_authenticated or not dealer: return False
        membership = Membership.objects.filter(user=request.user,dealer=dealer,is_active=True).first()
        request.membership = membership
        return bool(membership)

class CanManageInventory(IsDealerStaff):
    def has_permission(self, request, view):
        return super().has_permission(request,view) and request.membership.role in {Membership.Role.OWNER,Membership.Role.MANAGER}
