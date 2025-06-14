# api/serializers.py

from django.db import transaction # ! <<-- ایمپورت فراموش شده برای تراکنش
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import LabProfile, Project, Sample, SamplingSeries, Mold
from django.db.models import Sum, Q # برای محاسبات روی دیتابیس
from .models import Transaction # مدل جدید را ایمپورت کنید


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

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

class SamplingSeriesReadSerializer(serializers.ModelSerializer):
    # ! <<-- ۱. یک فیلد جدید برای نام محاسباتی تعریف می‌کنیم --!
    name = serializers.SerializerMethodField()
    
    # فیلد قبلی برای نمایش قالب‌ها
    molds = MoldSerializer(many=True, read_only=True)

    class Meta:
        model = SamplingSeries
        # ! <<-- ۲. نام فیلد جدید را به لیست فیلدها اضافه می‌کنیم --!
        fields = ['id', 'name', 'concrete_temperature', 'ambient_temperature', 'slump', 'range', 'air_percentage', 'has_additive', 'molds', 'sample']
    
    # ! <<-- ۳. متد محاسباتی برای تولید نام را پیاده‌سازی می‌کنیم --!
    def get_name(self, obj: SamplingSeries) -> str:
        """
        این متد نام ترتیبی هر سری نمونه را بر اساس ترتیب ساخت آن تولید می‌کند.
        """
        # اگر سری نمونه به هیچ نمونه‌ای وصل نبود (برای جلوگیری از خطا)
        if not obj.sample:
            return "سری نمونه نامشخص"
            
        # تمام سری‌های مربوط به همان نمونه را به ترتیب آی‌دی (زمان ساخت) می‌گیریم
        all_series_for_sample = obj.sample.series.order_by('id').all()
        
        # موقعیت (ایندکس) سری فعلی را در لیست پیدا می‌کنیم
        try:
            # تبدیل به لیست برای استفاده از متد index
            series_list = list(all_series_for_sample)
            index = series_list.index(obj)
            # ایندکس از صفر شروع می‌شود، پس ۱ واحد به آن اضافه می‌کنیم
            return f"سری نمونه {index + 1}"
        except ValueError:
            # اگر به هر دلیلی پیدا نشد
            return "سری نمونه ؟"
        
class SampleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'
 
class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('owner', 'created_at')

class SampleReadSerializer(SampleWriteSerializer):
    series = SamplingSeriesReadSerializer(many=True, read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True) # لیست تراکنش‌ها
    # ! <<-- فیلدهای محاسباتی برای خلاصه مالی --!
    total_income = serializers.SerializerMethodField()
    total_expense = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    class Meta(ProjectWriteSerializer.Meta):
        # فیلدهای جدید را به لیست فیلدها اضافه می‌کنیم
        fields = ProjectWriteSerializer.Meta.fields + ['transactions', 'total_income', 'total_expense', 'balance']

    def get_total_income(self, obj: Project):
        # با استفاده از aggregate، جمع تمام واریزی‌ها را از دیتابیس محاسبه می‌کنیم
        total = obj.transactions.filter(type='income').aggregate(total=Sum('amount'))['total']
        return total or 0.0

    def get_total_expense(self, obj: Project):
        total = obj.transactions.filter(type='expense').aggregate(total=Sum('amount'))['total']
        return total or 0.0
    
    def get_balance(self, obj: Project):
        income = self.get_total_income(obj)
        expense = self.get_total_expense(obj)
        return income - expense

class ProjectReadSerializer(ProjectWriteSerializer):
    samples = SampleReadSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M:%S")

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
    
class UserForFullDataSerializer(serializers.ModelSerializer):
    lab_profile = LabProfileSerializer(read_only=True)
    class Meta: model = User; fields = ['id', 'username', 'first_name', 'last_name', 'email', 'lab_profile']

class FullUserDataSerializer(serializers.Serializer):
    user = UserForFullDataSerializer()
    projects = ProjectReadSerializer(many=True)

