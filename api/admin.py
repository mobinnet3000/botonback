# api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import LabProfile, Project, Sample, SamplingSeries, Mold

# --- مدیریت یکپارچه User و LabProfile ---

# ابتدا مدل پیش‌فرض User را از حالت ثبت خارج می‌کنیم
admin.site.unregister(User)

# یک Inline برای LabProfile می‌سازیم تا در صفحه User نمایش داده شود
class LabProfileInline(admin.StackedInline):
    model = LabProfile
    can_delete = False
    verbose_name_plural = 'پروفایل آزمایشگاه'
    fk_name = 'user'
    # فیلدها را برای نمایش بهتر دسته‌بندی می‌کنیم
    fieldsets = (
        (None, {
            'fields': ('lab_name', 'lab_mobile_number', 'lab_phone_number')
        }),
        ('اطلاعات مکانی', {
            'fields': ('province', 'city', 'lab_address')
        }),
        ('اطلاعات اضافی', {
            'fields': ('telegram_id',)
        }),
    )

# یک کلاس ادمین سفارشی برای User می‌سازیم
class CustomUserAdmin(BaseUserAdmin):
    inlines = (LabProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_lab_name')

    def get_lab_name(self, instance):
        # یک ستون جدید برای نمایش نام آزمایشگاه در لیست کاربران
        try:
            return instance.lab_profile.lab_name
        except LabProfile.DoesNotExist:
            return "پروفایل آزمایشگاه ندارد"
    get_lab_name.short_description = 'نام آزمایشگاه'

# مدل User را با ادمین سفارشی خودمان دوباره ثبت می‌کنیم
admin.site.register(User, CustomUserAdmin)


# --- مدیریت پیشرفته مدل‌های دیگر ---

class MoldInline(admin.TabularInline):
    model = Mold
    extra = 0 # به صورت پیش‌فرض هیچ فرم خالی اضافه‌ای نمایش نده
    fields = ('sample_identifier', 'age_in_days', 'deadline', 'mass', 'breaking_load', 'completed_at')
    readonly_fields = ('created_at',)

@admin.register(SamplingSeries)
class SamplingSeriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'sample_info', 'concrete_temperature', 'slump', 'has_additive')
    list_filter = ('has_additive',)
    inlines = [MoldInline] # نمایش قالب‌ها در صفحه جزئیات سری نمونه

    def sample_info(self, obj):
        return f"نمونه ID: {obj.sample.id} (پروژه: {obj.sample.project.project_name})"
    sample_info.short_description = 'اطلاعات نمونه'

class SamplingSeriesInline(admin.TabularInline):
    model = SamplingSeries
    extra = 0
    fields = ('concrete_temperature', 'ambient_temperature', 'slump', 'has_additive')

@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'date', 'test_type', 'category')
    list_filter = ('test_type', 'category', 'date')
    search_fields = ('project__project_name', 'test_type')
    inlines = [SamplingSeriesInline]

class SampleInline(admin.TabularInline):
    model = Sample
    extra = 0
    fields = ('date', 'test_type', 'category')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # ستون‌هایی که در لیست پروژه‌ها نمایش داده می‌شود
    list_display = ('project_name', 'owner_lab_name', 'client_name', 'city', 'floor_count')
    
    # اضافه کردن قابلیت فیلتر بر اساس
    list_filter = ('owner__province', 'owner__city', 'project_usage_type', 'cement_type')
    
    # اضافه کردن نوار جستجو
    search_fields = ('project_name', 'client_name', 'owner__lab_name')
    
    # نمایش نمونه‌ها در صفحه جزئیات پروژه
    inlines = [SampleInline]
    
    # دسته‌بندی فیلدها در صفحه ویرایش/ساخت پروژه
    fieldsets = (
        ('اطلاعات اصلی پروژه', {
            'fields': ('owner', 'project_name', 'file_number', 'address')
        }),
        ('مشخصات فنی', {
            'fields': ('project_usage_type', 'floor_count', 'cement_type', 'occupied_area', 'mold_type')
        }),
        ('اشخاص مرتبط', {
            'classes': ('collapse',), # این گروه به صورت پیش‌فرض بسته باشد
            'fields': ('client_name', 'client_phone_number', 'supervisor_name', 'supervisor_phone_number', 'requester_name', 'requester_phone_number')
        }),
    )

    def owner_lab_name(self, obj):
        # نمایش نام آزمایشگاه مالک
        return obj.owner.lab_name
    owner_lab_name.short_description = 'آزمایشگاه مالک'

    def city(self, obj):
        # نمایش شهر آزمایشگاه مالک
        return obj.owner.city
    city.short_description = 'شهر'