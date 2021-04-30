from django.contrib.auth.models import User


def get_user_from_request(request):
    if not request.user.is_authenticated:
        return None
    return User.objects.get(pk=request.user.pk)
