# Generated by Django 4.2.20 on 2025-04-26 11:58

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('players', '0016_remove_cricketmatchstat_match_format_override_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Rating Score (1-5)')),
                ('rated_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='players.videoupload')),
            ],
            options={
                'ordering': ['-rated_at'],
                'unique_together': {('video', 'user')},
            },
        ),
    ]
