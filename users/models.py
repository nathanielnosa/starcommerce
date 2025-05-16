from django.db import models
from django.contrib.auth.models import User


GENDER_CHOICES=(
    ('M','Male'),
    ('F','Female'),
)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=15,null=True,blank=True)
    gender = models.CharField(max_length=6,choices=GENDER_CHOICES)
    image = models.ImageField(upload_to='profile',null=True,blank=True,default="https://png.pngtree.com/png-vector/20190329/ourmid/pngtree-vector-avatar-icon-png-image_889567.jpg")
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.fullname
