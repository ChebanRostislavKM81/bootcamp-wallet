from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class Users(AbstractBaseUser):
    first_name = models.TextField(verbose_name="first_name")
    last_name = models.TextField(verbose_name="last_name")
    birth_date = models.TextField(verbose_name="birth_date")
    email = models.EmailField(verbose_name="email", unique=True)
    password = models.TextField(verbose_name="password")

    USERNAME_FIELD = 'email'

    class Meta:
        db_table = "users"

objects = Users

