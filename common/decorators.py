from django.http import HttpResponse

def allowed_roles(groups = []):
    def decorator(view_function):
        def wrapper_function(request, *args, **kwargs):
            group = None

            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in groups:
                return view_function(request, *args, **kwargs)
            else:
                return HttpResponse('Authorization denied: Your group membership does not allow you access to this page. Please contact your IT administrator for additional information.')

        return wrapper_function
    return decorator
