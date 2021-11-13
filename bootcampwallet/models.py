from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class Users(AbstractBaseUser):
    first_name = models.TextField(verbose_name="first_name")
    last_name = models.TextField(verbose_name="last_name")
    birth_date = models.TextField(verbose_name="birth_date")
    email = models.EmailField(verbose_name="email", unique=True)
    password = models.TextField(verbose_name="password")
    balance = models.FloatField(verbose_name="balance")

    USERNAME_FIELD = 'email'

    class Meta:
        db_table = "users"

objects = Users

class Transactions(models.Model):
    type_of_transaction = models.TextField(verbose_name="type_of_transaction")
    user_id = models.IntegerField(verbose_name="user_id")
    secondary_email = models.EmailField(verbose_name="secondary_email", null=True)
    value = models.FloatField(verbose_name="value")
    date = models.DateField(verbose_name="date")

    class Meta:
        db_table = "transactions"

