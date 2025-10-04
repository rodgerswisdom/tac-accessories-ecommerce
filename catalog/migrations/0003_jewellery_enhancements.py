# Generated manually for jewellery enhancements

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_enhance_models'),
    ]

    operations = [
        # Create Tag model
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(max_length=60, unique=True)),
                ('color', models.CharField(default='#FFD700', help_text='Hex color for tag display', max_length=7)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
                'ordering': ['name'],
            },
        ),
        
        # Add gender field to Category
        migrations.AddField(
            model_name='category',
            name='gender',
            field=models.CharField(choices=[('unisex', 'Unisex'), ('men', 'Men'), ('women', 'Women')], default='unisex', max_length=10),
        ),
        
        # Add jewellery-specific fields to Product
        migrations.AddField(
            model_name='product',
            name='material',
            field=models.CharField(choices=[('gold', 'Gold'), ('silver', 'Silver'), ('platinum', 'Platinum'), ('diamond', 'Diamond'), ('gemstone', 'Gemstone'), ('pearl', 'Pearl'), ('other', 'Other')], default='gold', max_length=20),
        ),
        migrations.AddField(
            model_name='product',
            name='carat',
            field=models.CharField(blank=True, help_text='Gold carat (e.g., 18K, 24K)', max_length=10),
        ),
        migrations.AddField(
            model_name='product',
            name='stone_type',
            field=models.CharField(blank=True, help_text='Type of stone (diamond, ruby, etc.)', max_length=50),
        ),
        migrations.AddField(
            model_name='product',
            name='stone_count',
            field=models.PositiveIntegerField(default=0, help_text='Number of stones'),
        ),
        migrations.AddField(
            model_name='product',
            name='size',
            field=models.CharField(blank=True, help_text='Ring size, chain length, etc.', max_length=20),
        ),
        migrations.AddField(
            model_name='product',
            name='gallery_images',
            field=models.JSONField(blank=True, default=list, help_text='Additional product images'),
        ),
        migrations.AddField(
            model_name='product',
            name='is_new',
            field=models.BooleanField(default=False, help_text='Mark as new arrival'),
        ),
        migrations.AddField(
            model_name='product',
            name='is_bestseller',
            field=models.BooleanField(default=False, help_text='Mark as bestseller'),
        ),
        
        # Create many-to-many relationship between Product and Tag
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='products', to='catalog.tag'),
        ),
    ]
