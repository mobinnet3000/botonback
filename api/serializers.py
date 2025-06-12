# api/serializers.py

from django.db import transaction # ! <<-- ایمپورت فراموش شده برای تراکنش
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import LabProfile, Project, Sample, SamplingSeries, Mold

# --- سریالایزر ثبت نام ---
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    این سریالایزر فقط برای گرفتن دیتا و ساختن کاربر استفاده می‌شود (فقط نوشتن).
    """
    lab_name = serializers.CharField(required=True, write_only=True)
    lab_mobile_number = serializers.CharField(required=True, write_only=True)
    lab_address = serializers.CharField(required=True, write_only=True)
    province = serializers.CharField(required=True, write_only=True)
    city = serializers.CharField(required=True, write_only=True)
    lab_phone_number = serializers.CharField(required=False, allow_blank=True, write_only=True)
    telegram_id = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    class Meta:
        model = User
        # در Meta فقط فیلدهایی را نگه می‌داریم که مستقیماً روی مدل User هستند.
        fields = ['username', 'password', 'first_name', 'last_name', 'email',
                  # فیلدهای زیر فقط در ورودی دریافت می‌شوند و در Meta نیستند
                  'lab_name', 'lab_mobile_number', 'lab_address', 'province',
                  'city', 'lab_phone_number', 'telegram_id']
        
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @transaction.atomic # تضمین می‌کند که User و LabProfile با هم ساخته می‌شوند یا هیچکدام
    def create(self, validated_data):
        profile_data = {
            'lab_name': validated_data.pop('lab_name'),
            'lab_mobile_number': validated_data.pop('lab_mobile_number'),
            'lab_address': validated_data.pop('lab_address'),
            'province': validated_data.pop('province'),
            'city': validated_data.pop('city'),
            'lab_phone_number': validated_data.pop('lab_phone_number', ''),
            'telegram_id': validated_data.pop('telegram_id', None)
        }
        
        user = User.objects.create_user(**validated_data)
        LabProfile.objects.create(user=user, **profile_data)
        return user

# --- سریالایزرهای CRUD ---

class MoldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mold
        fields = '__all__'

class SamplingSeriesWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SamplingSeries
        fields = '__all__'

class SamplingSeriesReadSerializer(SamplingSeriesWriteSerializer):
    molds = MoldSerializer(many=True, read_only=True)

class SampleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'

class SampleReadSerializer(SampleWriteSerializer):
    series = SamplingSeriesReadSerializer(many=True, read_only=True)

class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('owner',)

class ProjectReadSerializer(ProjectWriteSerializer):
    samples = SampleReadSerializer(many=True, read_only=True)

class LabProfileSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    
    class Meta:
        model = LabProfile
        fields = ['id', 'lab_name', 'lab_phone_number', 'lab_mobile_number', 
                  'lab_address', 'province', 'city', 'telegram_id', 
                  'first_name', 'last_name', 'email', 'user']
        read_only_fields = ('user',)

    def update(self, instance, validated_data):
        # آپدیت همزمان User و LabProfile
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            user = instance.user
            
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.email = user_data.get('email', user.email)
            user.save()
        
        return super().update(instance, validated_data)
    
# api/serializers.py

# --- سریالایزر اندپوینت جامع Full-Data ---
class UserForFullDataSerializer(serializers.ModelSerializer):
    lab_profile = LabProfileSerializer(read_only=True)
    class Meta: model = User; fields = ['id', 'username', 'first_name', 'last_name', 'email', 'lab_profile']

class FullUserDataSerializer(serializers.Serializer):
    user = UserForFullDataSerializer()
    projects = ProjectReadSerializer(many=True)