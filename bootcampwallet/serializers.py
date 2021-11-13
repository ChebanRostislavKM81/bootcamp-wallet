from rest_framework import serializers
from . import models
class Registration(serializers.ModelSerializer):
    class Meta:
        model = models.Users
        fields = (
            "first_name",
            "last_name",
            "birth_date",
            "email",
            "password",
        )

    def save(self):
        acc = models.Users(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            birth_date=self.validated_data['birth_date'],
            email=self.validated_data['email'],
            balance = 0.0
                           )
        extra_kwargs = {"password":{"write_only":True}}
        password = self.validated_data['password']
        acc.set_password(password)
        acc.save()
        return acc

class updating_balance(serializers.ModelSerializer):
    class Meta:
        model = models.Transactions
