# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    TransactionViewSet, UserRegistrationView, FullUserDataView, LabProfileViewSet, ProjectViewSet, 
    SampleViewSet, SamplingSeriesViewSet, MoldViewSet,
    TicketViewSet, TicketMessageViewSet # ✅ ویوهای جدید ایمپورت شدند
)

router = DefaultRouter()
router.register(r'profiles', LabProfileViewSet, basename='profile')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'samples', SampleViewSet, basename='sample')
router.register(r'series', SamplingSeriesViewSet, basename='series')
router.register(r'molds', MoldViewSet, basename='mold')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'tickets', TicketViewSet, basename='ticket') # ✅ اندپوینت تیکت‌ها
router.register(r'ticket-messages', TicketMessageViewSet, basename='ticket-message') # ✅ اندپوینت پیام‌ها


urlpatterns = [
    # اندپوینت‌های CRUD
    path('', include(router.urls)),
    
    # اندپوینت‌های اصلی
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('full-data/', FullUserDataView.as_view(), name='full-data'),
]