# Generated manually for enhanced models

from django.db import migrations, models
import django.db.models.deletion
import django.utils.text
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        # Add new fields to Category
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='categories/'),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='catalog.category'),
        ),
        migrations.AddField(
            model_name='category',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='category',
            name='sort_order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='category',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        
        # Add new fields to Product
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='short_description',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='product',
            name='compare_price_cents',
            field=models.PositiveIntegerField(blank=True, help_text='Original price for showing discounts', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.CharField(blank=True, help_text='Stock Keeping Unit', max_length=50, unique=True),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='low_stock_threshold',
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.AddField(
            model_name='product',
            name='track_inventory',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='weight_grams',
            field=models.PositiveIntegerField(default=0, help_text='Weight in grams for shipping calculations'),
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/'),
        ),
        migrations.AddField(
            model_name='product',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='products/thumbnails/'),
        ),
        migrations.AddField(
            model_name='product',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        
        # Update Category Meta
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['sort_order', 'name'], 'verbose_name_plural': 'Categories'},
        ),
    ]
