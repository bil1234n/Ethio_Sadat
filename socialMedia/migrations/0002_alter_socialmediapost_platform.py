# Generated: adds "telegram" as a manageable platform (replaces the old RSS feed)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialMedia', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialmediapost',
            name='platform',
            field=models.CharField(choices=[('instagram', 'Instagram'), ('facebook', 'Facebook'), ('tiktok', 'TikTok'), ('telegram', 'Telegram')], default='facebook', max_length=20),
        ),
    ]
