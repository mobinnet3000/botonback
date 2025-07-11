# Generated by Django 5.2.3 on 2025-06-12 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_project_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='address',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='project',
            name='cement_type',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='project',
            name='client_name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='project',
            name='client_phone_number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='project',
            name='floor_count',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='project',
            name='mold_type',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='project',
            name='municipality_zone',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='project',
            name='occupied_area',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_usage_type',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='project',
            name='requester_name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='project',
            name='requester_phone_number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='project',
            name='supervisor_name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='project',
            name='supervisor_phone_number',
            field=models.CharField(max_length=20),
        ),
    ]
