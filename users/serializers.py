from rest_framework import serializers
from . models import Profile
from django.contrib.auth.models import User

from . utils import SendMail

# serialize django user
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields = ['username','email']

# serialize profile
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= UserSerializer()
        fields = ['fullname','gender','phone','image']

# registration serializer
class RegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    class Meta:
        model = Profile
        fields = ['fullname','username','email','password1','password2','gender','phone','image']
    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Password not match')
        return data
    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password1')
        
        user = User.objects.create_user(username=username,email=email,password=password)

        profile = Profile.objects.create(
            user=user,
            fullname = validated_data['fullname'],
            phone = validated_data['phone'],
            gender = validated_data['gender'],
            image = validated_data.get('image'),
        )
        SendMail(email,profile.fullname)
        return profile
    
