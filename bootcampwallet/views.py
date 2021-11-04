from django.db import models
from . import serializers
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST',])
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
    else:
        data['response'] = serializer.errors
    return Response(data)
