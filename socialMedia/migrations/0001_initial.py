# Generated for the SocialMediaPost admin-managed model

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SocialMediaPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('instagram', 'Instagram'), ('facebook', 'Facebook'), ('tiktok', 'TikTok')], default='facebook', max_length=20)),
                ('link', models.URLField(max_length=500)),
                ('image', models.ImageField(blank=True, null=True, upload_to='social_media_posts/')),
                ('caption', models.TextField(blank=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-date', '-created_at'],
            },
        ),
    ]
