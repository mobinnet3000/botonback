# api/admin.py
from django.contrib import admin
from .models import LabProfile, Project, Sample, SamplingSeries, Mold

admin.site.register(LabProfile)
admin.site.register(Project)
admin.site.register(Sample)
admin.site.register(SamplingSeries)
admin.site.register(Mold)