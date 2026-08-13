# Generated for the SiteSettings singleton (admin-editable Telegram order username)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_order_username', models.CharField(default='Ahamuti', help_text='Telegram username that receives product orders. Do not include the @ symbol.', max_length=100)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
