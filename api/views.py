# api/views.py
from rest_framework import viewsets, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import LabProfile, Project, Sample, SamplingSeries, Mold, Transaction,Ticket, TicketMessage
from .serializers import (
    TransactionSerializer, UserRegistrationSerializer, LabProfileSerializer, ProjectReadSerializer, ProjectWriteSerializer,
    SampleReadSerializer, SampleWriteSerializer, SamplingSeriesReadSerializer,
    SamplingSeriesWriteSerializer, MoldSerializer, FullUserDataSerializer
        ,TicketSerializer, TicketMessageSerializer # ✅ سریالایزرهای جدید ایمپورت شدند

)

# --- ویوهای اصلی ---
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

class FullUserDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        data = {'user': request.user, 'projects': Project.objects.filter(owner__user=request.user)}
        serializer = FullUserDataSerializer(data)
        return Response(serializer.data)

# --- ViewSet های CRUD ---
class LabProfileViewSet(viewsets.ModelViewSet):
    serializer_class = LabProfileSerializer
    def get_queryset(self): return LabProfile.objects.filter(user=self.request.user)

class ProjectViewSet(viewsets.ModelViewSet):
    def get_queryset(self): return Project.objects.filter(owner__user=self.request.user)
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']: return ProjectReadSerializer
        return ProjectWriteSerializer
    def perform_create(self, serializer): serializer.save(owner=self.request.user.lab_profile)

class SampleViewSet(viewsets.ModelViewSet):
    def get_queryset(self): return Sample.objects.filter(project__owner__user=self.request.user)
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']: return SampleReadSerializer
        return SampleWriteSerializer

class SamplingSeriesViewSet(viewsets.ModelViewSet):
    def get_queryset(self): return SamplingSeries.objects.filter(sample__project__owner__user=self.request.user)
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']: return SamplingSeriesReadSerializer
        return SamplingSeriesWriteSerializer

class MoldViewSet(viewsets.ModelViewSet):
    serializer_class = MoldSerializer
    def get_queryset(self): return Mold.objects.filter(series__sample__project__owner__user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # هر کاربر فقط تراکنش‌های پروژه‌های خودش را می‌بیند
        return Transaction.objects.filter(project__owner__user=self.request.user)
class TicketViewSet(viewsets.ModelViewSet):
    """
    این ViewSet به کاربران اجازه می‌دهد تیکت‌های خود را مدیریت کنند.
    """
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        هر کاربر فقط تیکت‌های خودش را می‌بیند.
        """
        return Ticket.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        """
        هنگام ساخت تیکت جدید، کاربر به صورت خودکار کاربر لاگین شده تعیین می‌شود.
        """
        serializer.save(user=self.request.user)

class TicketMessageViewSet(viewsets.ModelViewSet):
    """
    این ViewSet اجازه می‌دهد کاربران به تیکت‌های خود پیام اضافه کنند.
    """
    serializer_class = TicketMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        کاربران فقط پیام‌های مربوط به تیکت‌های خودشان را می‌بینند.
        """
        return TicketMessage.objects.filter(ticket__user=self.request.user).order_by('created_at')
    
    def perform_create(self, serializer):
        """
        هنگام ارسال پیام، کاربر به صورت خودکار کاربر لاگین شده تعیین می‌شود.
        """
        # TODO: در حالت پیشرفته‌تر، باید چک کرد که آیا کاربر اجازه ارسال پیام به این تیکت را دارد یا خیر.
        serializer.save(user=self.request.user)
