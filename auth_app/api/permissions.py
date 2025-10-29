from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """JWT authentication that falls back to an access token stored in cookies.

    If no Authorization header is present, this class will look for an
    `access_token` cookie and return it as if it were a Bearer token. This is
    useful when the frontend stores tokens in HttpOnly cookies and you want
    DRF's authentication classes to pick them up automatically.
    """

    def get_header(self, request):
        header = super().get_header(request)
        if header is None:
            token = request.COOKIES.get('access_token')
            if token:
                # Return the header bytes as JWTAuthentication expects.
                return f'Bearer {token}'.encode()
        return header