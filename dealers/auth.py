from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Membership

def dealer_role_required(*roles):
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.dealer: raise PermissionDenied("No dealer selected.")
            membership = Membership.objects.filter(dealer=request.dealer, user=request.user, is_active=True).first()
            if not membership or membership.role not in roles: raise PermissionDenied
            request.membership = membership
            return view(request, *args, **kwargs)
        return wrapped
    return decorator
