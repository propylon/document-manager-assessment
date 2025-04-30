import logging

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from propylon_document_manager.utils.status_code import StatusCode

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        '''
        Removes the refresh token and access token from the response and sets it in the cookie
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        response = super().post(request, *args, **kwargs)

        response.data.update({'user': request.data.get('email')} | StatusCode.get_response(200))
        access = response.data.pop("access", None)
        refresh = response.data.pop("refresh", None)

        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=True,  # Set to True in production
            samesite="None",
            # domain='localhost:3000'
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,  # Set to True in production
            samesite="None",
            # domain='localhost:3000'
        )
        return response


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = []

    def post(self, request, *args, **kwargs) -> Response:
        '''
        Based on the refresh token, it generates a new access token and sets it in the cookie
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(StatusCode.get_response(401))
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.exception('Exception in Refresh Token', e)
            return Response(StatusCode.get_response(401))

        response = Response(StatusCode.get_response(200))
        access = serializer.validated_data['access']
        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=True,  # Set to True in production
            samesite="None",
        )
        return response


class LogoutView(APIView):
    def get(self, request, *args, **kwargs) -> Response:
        '''
        Logout the user by deleting the access and refresh tokens from the cookies.
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        response = Response(StatusCode.get_response(202))
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
