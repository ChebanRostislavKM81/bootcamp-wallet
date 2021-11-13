from django.contrib.auth.hashers import check_password
from . import serializers
from . import models
from django.contrib.auth import login, logout, authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from django.core.exceptions import ValidationError
from datetime import date
from django.db.models import F



@api_view(['POST',])
@authentication_classes([TokenAuthentication])
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
@authentication_classes([TokenAuthentication])
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
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logging_out(request):
    token = request.user.auth_token
    request.user.auth_token.delete()
    logout(request)
    return Response(status=204)



@api_view(['POST',])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def fill(request):

    data = {}

    value = request.data["value"]
    if (type(value)!=int and type(value)!=float) or value <= 0.0 :
        return Response(status=400)

    new_transaction = models.Transactions(
        type_of_transaction="fill",
        user_id=request.user.id,
        secondary_email=None,
        value=value,
        date=date.today()
    )

    new_transaction.save()
    change_balance = models.Users.objects.get(email=request.user.email)
    change_balance.balance = F('balance') + value
    change_balance.save()

    data["balance"] = request.user.balance


    return Response(data)

@api_view(['POST',])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def withdraw(request):

    data = {}

    value = request.data["value"]
    if (type(value)!=int and type(value)!=float) or value <= 0.0 :
        return Response(status=400)

    if request.user.balance < value:
        return Response(status=400)

    new_transaction = models.Transactions(
        type_of_transaction="withdraw",
        user_id=request.user.id,
        secondary_email=None,
        value=value,
        date=date.today()
    )

    new_transaction.save()
    change_balance = models.Users.objects.get(email=request.user.email)
    change_balance.balance = F('balance') - value
    change_balance.save()

    data["balance"] = request.user.balance

    return Response(data)
