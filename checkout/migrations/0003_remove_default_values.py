# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0002_enhance_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='county',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='address',
            name='country',
            field=models.CharField(max_length=60),
        ),
    ]
