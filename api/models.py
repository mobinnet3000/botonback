# api/models.py

from django.db import models
from django.contrib.auth.models import User

class LabProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lab_profile')
    lab_name = models.CharField(max_length=200, verbose_name="نام آزمایشگاه")
    lab_phone_number = models.CharField(max_length=20, verbose_name="شماره آزمایشگاه", blank=True)
    lab_mobile_number = models.CharField(max_length=20, verbose_name="موبایل آزمایشگاه")
    lab_address = models.TextField(verbose_name="آدرس آزمایشگاه")
    province = models.CharField(max_length=100, verbose_name="استان")
    city = models.CharField(max_length=100, verbose_name="شهر")
    telegram_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="آیدی تلگرام")
    def __str__(self): return self.lab_name

class Project(models.Model):
    owner = models.ForeignKey(LabProfile, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ساخت پروژه")
    file_number = models.CharField(max_length=100, verbose_name="شماره پرونده")
    project_name = models.CharField(max_length=255, verbose_name="نام پروژه")
    client_name = models.CharField(max_length=200, verbose_name="نام کارفرما")
    client_phone_number = models.CharField(max_length=20, verbose_name="شماره تماس کارفرما")
    supervisor_name = models.CharField(max_length=200, verbose_name="نام ناظر")
    supervisor_phone_number = models.CharField(max_length=20, verbose_name="شماره تماس ناظر")
    requester_name = models.CharField(max_length=200, verbose_name="نام درخواست دهنده")
    requester_phone_number = models.CharField(max_length=20, verbose_name="شماره تماس درخواست دهنده")
    municipality_zone = models.CharField(max_length=100, verbose_name="منطقه شهرداری")
    address = models.TextField(verbose_name="آدرس")
    project_usage_type = models.CharField(max_length=100, verbose_name="کاربری پروژه")
    floor_count = models.IntegerField(verbose_name="طبقات")
    cement_type = models.CharField(max_length=100, verbose_name="نوع سیمان")
    occupied_area = models.FloatField(verbose_name="سطح زیربنا اشغال شده")
    mold_type = models.CharField(max_length=100, verbose_name="نوع قالب")
    client_name = models.CharField(max_length=200); client_phone_number = models.CharField(max_length=20); supervisor_name = models.CharField(max_length=200); supervisor_phone_number = models.CharField(max_length=20); requester_name = models.CharField(max_length=200); requester_phone_number = models.CharField(max_length=20); municipality_zone = models.CharField(max_length=100); address = models.TextField(); project_usage_type = models.CharField(max_length=100); floor_count = models.IntegerField(); cement_type = models.CharField(max_length=100); occupied_area = models.FloatField(); mold_type = models.CharField(max_length=100)
    contract_price = models.DecimalField(max_digits=20, decimal_places=2, default=0.0, verbose_name="مبلغ کل قرارداد")

    def __str__(self): return self.project_name

class Sample(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='samples')
    date = models.DateTimeField(verbose_name="تاریخ")
    test_type = models.CharField(max_length=100, verbose_name="نوع آزمون")
    sampling_volume = models.CharField(max_length=50, verbose_name="حجم نمونه برداری")
    cement_grade = models.CharField(max_length=50, verbose_name="عیار سیمان")
    category = models.CharField(max_length=100, verbose_name="رده")
    weather_condition = models.CharField(max_length=100, verbose_name="وضعیت جوی")
    concrete_factory = models.CharField(max_length=200, verbose_name="کارخانه بتن")
    def __str__(self): return f"نمونه برای {self.project.project_name}"

class SamplingSeries(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='series')
    concrete_temperature = models.FloatField(verbose_name="دمای بتن")
    ambient_temperature = models.FloatField(verbose_name="دمای محیط")
    slump = models.FloatField()
    range = models.CharField(max_length=50, verbose_name="محدوده")
    air_percentage = models.FloatField(verbose_name="درصد هوا")
    has_additive = models.BooleanField(default=False, verbose_name="داشتن افزودنی")
    class Meta: verbose_name_plural = "Sampling Series"
    def __str__(self): return f"سری برای نمونه {self.sample.id}"

class Mold(models.Model):
    series = models.ForeignKey(SamplingSeries, on_delete=models.CASCADE, related_name='molds')
    age_in_days = models.IntegerField(verbose_name="چند روزه")
    mass = models.FloatField(verbose_name="جرم")
    breaking_load = models.FloatField(verbose_name="بار گسیختگی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد شدن")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="زمان انجام")
    deadline = models.DateTimeField(verbose_name="زمان ددلاین")
    sample_identifier = models.CharField(max_length=100, verbose_name="نمونه قالب")
    extra_data = models.JSONField(blank=True, null=True, verbose_name="دیتا اضافی")
    def __str__(self): return f"قالب {self.sample_identifier}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'واریزی'),
        ('expense', 'هزینه/برداشت'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='transactions', verbose_name="پروژه")
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, verbose_name="نوع تراکنش")
    description = models.TextField(verbose_name="توضیحات")
    # برای مبالغ مالی همیشه از DecimalField استفاده کنید تا خطای اعشار رخ ندهد
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مبلغ")
    date = models.DateTimeField(verbose_name="تاریخ تراکنش")

    def __str__(self):
        return f"{self.get_type_display()} - {self.project.project_name}"
    

# ✅✅✅ مدل‌های جدید برای سیستم تیکتینگ ✅✅✅
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'باز'),
        ('in_progress', 'در حال بررسی'),
        ('closed', 'بسته شده'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'پایین'),
        ('medium', 'متوسط'),
        ('high', 'بالا'),
    ]

    title = models.CharField(max_length=255, verbose_name="عنوان تیکت")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets', verbose_name="کاربر")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="وضعیت")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="اولویت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    def __str__(self):
        return f"تیکت: {self.title} ({self.user.username})"

class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages', verbose_name="تیکت")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    message = models.TextField(verbose_name="متن پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    def __str__(self):
        return f"پیام از {self.user.username} برای تیکت {self.ticket.id}"
