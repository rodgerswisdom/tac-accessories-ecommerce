# Generated manually for accounts models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('email_verified', models.BooleanField(default=False)),
                ('phone_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Customer Profile',
                'verbose_name_plural': 'Customer Profiles',
            },
        ),
        migrations.CreateModel(
            name='CustomerAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_type', models.CharField(choices=[('billing', 'Billing'), ('shipping', 'Shipping'), ('both', 'Both')], default='shipping', max_length=10)),
                ('full_name', models.CharField(max_length=120)),
                ('phone', models.CharField(max_length=30)),
                ('line1', models.CharField(max_length=120, verbose_name='Address Line 1')),
                ('line2', models.CharField(blank=True, max_length=120, verbose_name='Address Line 2')),
                ('city', models.CharField(max_length=60)),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('county', models.CharField(default='Nairobi', max_length=60)),
                ('country', models.CharField(default='Kenya', max_length=60)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Customer Address',
                'verbose_name_plural': 'Customer Addresses',
                'ordering': ['-is_default', '-created_at'],
            },
        ),
    ]
