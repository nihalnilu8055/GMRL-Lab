# Generated by Django 5.0.2 on 2024-04-12 05:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('date', models.DateField(max_length=255)),
                ('time', models.TextField(max_length=255)),
                ('age', models.CharField(max_length=255)),
                ('gender', models.CharField(max_length=255)),
                ('address', models.TextField(max_length=255)),
                ('message', models.TextField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('image', models.CharField(max_length=3000)),
                ('address', models.TextField(max_length=500)),
                ('number', models.IntegerField()),
                ('email', models.CharField(max_length=255)),
                ('status', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Enquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('message', models.TextField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Branch_time',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opening_hours', models.CharField(max_length=300)),
                ('closing_hours', models.CharField(max_length=300)),
                ('opening_week', models.CharField(max_length=300)),
                ('closing_week', models.CharField(max_length=300, null=True)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.branch')),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('image', models.CharField(max_length=3055)),
                ('price', models.IntegerField()),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.branch')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, verbose_name='Customer Name')),
                ('amount', models.FloatField(verbose_name='Amount')),
                ('status', models.CharField(default='Pending', max_length=254, verbose_name='Payment Status')),
                ('provider_order_id', models.CharField(max_length=40, verbose_name='Order ID')),
                ('payment_id', models.CharField(max_length=36, verbose_name='Payment ID')),
                ('signature_id', models.CharField(max_length=128, verbose_name='Signature ID')),
                ('branch_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.branch')),
                ('package_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.package')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('email', models.CharField(max_length=300)),
                ('age', models.CharField(max_length=300)),
                ('address', models.TextField(max_length=500)),
                ('gender', models.CharField(max_length=300)),
                ('number', models.CharField(max_length=300)),
                ('date', models.DateField(max_length=255)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subpackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=255)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.package')),
            ],
        ),
    ]