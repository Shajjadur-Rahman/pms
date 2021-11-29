from django.shortcuts import HttpResponseRedirect, reverse, render



class PermissionForAllUser:
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type == 'Admin' or request.user.user_type == 'Manager' or request.user.user_type == 'Member' or request.user.user_type == 'Contact':
            return super().dispatch(request, *args, **kwargs)
        return render(request, 'permission/permission_denied.html', context={'username': request.user.username})



class AdminAndManagerPermission:
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type == 'Admin' or request.user.user_type == 'Manager':
            return super().dispatch(request, *args, **kwargs)
        return render(request, 'permission/permission_denied.html', context={'username': request.user.username})

