# Generated by Django 5.0.11 on 2025-04-08 04:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visits', '0003_remove_visit_check_in_time_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='visit',
            name='requested_by',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'SECURITY'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requested_visits', to=settings.AUTH_USER_MODEL),
        ),
    ]
