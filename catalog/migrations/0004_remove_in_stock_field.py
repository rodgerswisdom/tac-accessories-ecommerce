# Generated manually to remove in_stock field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_jewellery_enhancements'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='in_stock',
        ),
    ]
