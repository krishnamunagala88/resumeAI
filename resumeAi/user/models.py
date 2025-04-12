from django.db import models

# class users(models.Model):
#     name = models.CharField(max_length = 255)
#     email = models.CharField(max_length = 255)
#     fee = models.IntegerField()



class users(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    fee = models.IntegerField()
    roles = models.ManyToManyField("userRoles.Role", related_name="users")  # Cross-app reference

    def __str__(self):
        return self.name