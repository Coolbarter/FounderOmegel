# Generated by Django 5.2.1 on 2025-05-15 14:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('match_score', models.FloatField(help_text='Similarity score between founders')),
                ('common_interests', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('scheduled_time', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('founder1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_founder1', to=settings.AUTH_USER_MODEL)),
                ('founder2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_founder2', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('founder1', 'founder2')},
            },
        ),
    ]
