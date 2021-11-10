from django.contrib.auth.hashers import check_password
from . import serializers
from . import models
from django.contrib.auth import login, logout, authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError

@api_view(['POST',])
@permission_classes([AllowAny])
def registration(request):

    serializer = serializers.Registration(data=request.data)
    data = {}
    if serializer.is_valid():

        acc = serializer.save()
        data['response'] = 'success'
        data['first_name'] = acc.first_name
        data['last_name'] = acc.last_name
        data['email'] = acc.email
        acc.save()
        AuthToken = Token.objects.get_or_create(user=acc)[0].key
        data['token'] = AuthToken
    else:

        data['response'] = serializer.errors

    return Response(data)


@api_view(['POST',])
@permission_classes([AllowAny])
def authentication(request):


    data = {}



    user_email = request.data["email"]
    user_password = request.data["password"]

    try:

        acc = models.Users.objects.get(email=user_email)
    except BaseException:
        raise ValidationError({"response": f"Invalid data"})
    AuthToken = Token.objects.get_or_create(user=acc)[0].key
    if not check_password(user_password, acc.password):
        raise ValidationError({"response": f"Invalid data"})
    if acc:

        login(request, acc)
        data["token"] = AuthToken

        return Response(data)
    else:
        raise ValidationError({"response": "Invalid data"})


@api_view(['POST',])
@permission_classes([IsAuthenticated])
def logging_out(request):
    AuthToken = request.user.auth_token
    request.user.auth_token.delete()
    logout(request)
    return Response(headers={"Authentication":AuthToken})









