from django.db import models
from django.contrib.auth.models import User

class video(models.Model):
    videofile=models.FileField(upload_to='videos/', null=True, verbose_name="")
    title=models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    def __str__(self):
        return str(self.videofile)
class user(models.Model):
    username=models.CharField(max_length=40)
    password=models.CharField(max_length=40)
    email = models.CharField(max_length=40)
    gender = models.CharField(max_length=10)
    birthdate=models.CharField(max_length=40)
    def __str__(self):
        return self.email

class search_images(models.Model):
    img=models.ImageField(upload_to="mo/static/SportsTube/search_images/")