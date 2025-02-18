from django.db import models

class users(models.Model):
    name = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    fee = models.IntegerField()