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
from datetime import date, datetime, timedelta
from django.db.models import F
import requests



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



    return Response(status=200)

@api_view(['POST',])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def withdraw(request):



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



    return Response(status=200)


@api_view(['POST',])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def pay(request):

    value = request.data["value"]
    if (type(value) != int and type(value) != float) or value <= 0.0:
        return Response(status=400)

    if request.user.balance < value:
        return Response(status=400)

    recipient_email = request.data["email"]

    if recipient_email == request.user.email:
        return Response(status=400)


    try:
        recipient = models.Users.objects.get(email=recipient_email)
    except:
        return Response(status=400)

    new_transaction = models.Transactions(
        type_of_transaction="pay",
        user_id=request.user.id,
        secondary_email=recipient_email,
        value=value,
        date=date.today()
    )

    new_transaction.save()

    new_transaction = models.Transactions(
        type_of_transaction="recieve",
        user_id=recipient.id,
        secondary_email=None,
        value=value,
        date=date.today()
    )

    new_transaction.save()

    change_balance = models.Users.objects.get(email=request.user.email)
    change_balance.balance = F('balance') - value
    change_balance.save()


    recipient.balance = F('balance') + value
    recipient.save()
    return Response(status=200)


@api_view(['GET',])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def get_transactions(request):

    try:
        start_date = request.query_params["start_date"]
    except:
        return Response(status=400)

    try:
        end_date = request.query_params["end_date"]
    except:
        return Response(status=400)

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    user_transactions = models.Transactions.objects.filter(user_id=request.user.id)

    list_of_transactions = []

    for transaction in user_transactions:

        if transaction.date >= start_date and transaction.date <= end_date:
            list_of_transactions.append(

                {
                "date" : transaction.date,
                "type" : transaction.type_of_transaction,
                "value" : transaction.value
                }

            )

    return Response({"transactions" : list_of_transactions})


@api_view(['GET',])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def get_balance(request):

    data = {}

    request_currency = request.query_params["currency"].upper()

    if request_currency != "EUR" and request_currency != "USD" and request_currency != "UAH":
        return Response(status=400)

    currency_api_url = "http://api.exchangeratesapi.io/v1/latest?access_key=767366a9c7b953b7d6f43e0e74e40329"
    currency_api = requests.get(currency_api_url).json()

    currency = currency_api['rates'][request_currency]

    data["balance"] = round(request.user.balance * currency, 2)

    return Response(data)


@api_view(['GET',])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def get_series(request):

    try:
        start_date = request.query_params["start_date"]
    except:
        return Response(status=400)

    try:
        end_date = request.query_params["end_date"]
    except:
        return Response(status=400)


    request_currency = request.query_params["currency"].upper()

    if request_currency != "EUR" and request_currency != "USD" and request_currency != "UAH":
        return Response(status=400)

    currency_api_url = "http://api.exchangeratesapi.io/v1/latest?access_key=767366a9c7b953b7d6f43e0e74e40329"
    currency_api = requests.get(currency_api_url).json()


    currency = currency_api['rates'][request_currency]


    data = {}

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    list_of_transactions = [[], [], [], [], []]


    for date in daterange(start_date, end_date + timedelta(1)):
        sum_fill, sum_withdraw, sum_pay, sum_recieve = 0.0, 0.0, 0.0, 0.0
        user_transactions = models.Transactions.objects.filter(user_id=request.user.id, date=date)



        for transaction in user_transactions:



            if transaction.type_of_transaction == "fill":
                sum_fill += (transaction.value * currency)


            elif transaction.type_of_transaction == "withdraw":
                sum_withdraw += (currency * transaction.value)

            elif transaction.type_of_transaction == "pay":
                sum_pay += (currency * transaction.value)

            else:

                sum_recieve += (currency * transaction.value)

        list_of_transactions[0].append(sum_fill)
        list_of_transactions[1].append(sum_withdraw)
        list_of_transactions[2].append(sum_pay)
        list_of_transactions[3].append(sum_recieve)
        list_of_transactions[4].append(date)



        data["filled"] = list_of_transactions[0]
        data["withdrawn"] = list_of_transactions[1]
        data["payments_made"] = list_of_transactions[2]
        data["payments_recieved"] = list_of_transactions[3]
        data["dates"] = list_of_transactions[4]

    return Response(data)



@api_view(['GET',])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def get_summary(request):

    try:
        start_date = request.query_params["start_date"]
    except:
        return Response(status=400)

    try:
        end_date = request.query_params["end_date"]
    except:
        return Response(status=400)

    request_currency = request.query_params["currency"].upper()

    if request_currency != "EUR" and request_currency != "USD" and request_currency != "UAH":
        return Response(status=400)

    currency_api_url = "http://api.exchangeratesapi.io/v1/latest?access_key=767366a9c7b953b7d6f43e0e74e40329"
    currency_api = requests.get(currency_api_url).json()

    currency = currency_api['rates'][request_currency]

    data = {}

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    user_transactions = models.Transactions.objects.filter(user_id=request.user.id)

    list_of_transactions = [[],[],[],[]]

    for transaction in user_transactions:

        if transaction.date >= start_date and transaction.date <= end_date:

            if transaction.type_of_transaction == "fill":
                list_of_transactions[0].append(round(transaction.value * currency,2))

            elif transaction.type_of_transaction == "withdraw":
                list_of_transactions[1].append(round(transaction.value * currency,2))

            elif transaction.type_of_transaction == "pay":
                list_of_transactions[2].append(round(transaction.value * currency,2))
            else:

                list_of_transactions[3].append(round(transaction.value * currency,2))



            data["filled"] = sum(list_of_transactions[0])
            data["withdrawn"] = sum(list_of_transactions[1])
            data["payments_made"] = sum(list_of_transactions[2])
            data["payments_recieved"] = sum(list_of_transactions[3])


    return Response(data)