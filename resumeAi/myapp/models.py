from django.db import models


class Student(models.Model):
    name = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    address = models.CharField(max_length = 255)
    user = models.CharField(max_length = 255)
    fee = models.IntegerField()
