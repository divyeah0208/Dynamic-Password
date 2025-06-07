from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField()
    image = models.ImageField(upload_to='images/')
    face_image = models.ImageField(upload_to='faces/')
    lang = models.CharField(max_length=100,null=True, blank=False)
    lat = models.CharField(max_length=100,null=True,blank=False)
    
