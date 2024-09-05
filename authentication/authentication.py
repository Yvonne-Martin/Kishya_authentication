from django.contrib.auth.models import User

class Auth0Backend:
    def authenticate(self, request, user_info=None):
        if user_info:
            user, created = User.objects.get_or_create(username=user_info['email'])
            if created:
                user.email = user_info['email']
                user.save()
            return user
        return None
