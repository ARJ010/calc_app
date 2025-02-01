from django.contrib.auth.models import Group

def is_admin(request):
    """Check if the current user belongs to the 'Admin' group."""
    return {'is_admin': request.user.groups.filter(name='Admin').exists()}
