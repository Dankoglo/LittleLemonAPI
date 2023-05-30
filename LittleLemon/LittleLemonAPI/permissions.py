from rest_framework.permissions import IsAuthenticated

class IsManager(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(
            super().has_permission(request, view) and request.user.groups.filter(name="Manager").exists()
        )
    
class IsCustomer(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(
            super().has_permission(request, view) and \
            not request.user.groups.filter(name="Manager").exists() and \
            not request.user.groups.filter(name="Delivery crew").exists()
        )

class IsEmployee(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(
            super().has_permission(request, view) and \
            (request.user.groups.filter(name="Manager").exists() or \
             request.user.groups.filter(name="Delivery crew").exists())
        )