from django.db import models


class User(models.Model):
    username = models.CharField(max_length=50, primary_key=True)
    password = models.CharField(max_length=200)
    token = models.CharField(max_length=32)
    ip_addr = models.CharField(max_length=15)
