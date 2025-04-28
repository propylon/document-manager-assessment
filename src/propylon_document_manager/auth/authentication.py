from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieAuthentication(JWTAuthentication):
    """
    Custom authentication class that uses JWT tokens stored in cookies.
    """

    def authenticate(self, request):
        """
        Authenticate the user by checking the JWT token in the cookies.
        """
        # Get the JWT token from the cookies
        token = request.COOKIES.get('access_token')

        if not token:
            return None

        # Decode the JWT token to get the user
        validated_token = self.get_validated_token(token)
        return self.get_user(validated_token), validated_token
