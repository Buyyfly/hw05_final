# Generated by Django 2.2.16 on 2022-06-09 17:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.query


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.query.QuerySet, related_name='follower', to=settings.AUTH_USER_MODEL),
        ),
    ]
