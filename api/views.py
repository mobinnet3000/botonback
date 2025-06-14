# api/views.py
from rest_framework import viewsets, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import LabProfile, Project, Sample, SamplingSeries, Mold, Transaction
from .serializers import (
    TransactionSerializer, UserRegistrationSerializer, LabProfileSerializer, ProjectReadSerializer, ProjectWriteSerializer,
    SampleReadSerializer, SampleWriteSerializer, SamplingSeriesReadSerializer,
    SamplingSeriesWriteSerializer, MoldSerializer, FullUserDataSerializer
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