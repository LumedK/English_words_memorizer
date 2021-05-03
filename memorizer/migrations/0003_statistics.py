# Generated by Django 3.2 on 2021-05-01 22:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('memorizer', '0002_auto_20210501_1753'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run', models.IntegerField()),
                ('completed', models.IntegerField()),
                ('failed', models.IntegerField()),
                ('date', models.DateField(auto_now=True)),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memorizer.memorizingline')),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memorizer.memorizinglist')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memorizer.word')),
            ],
        ),
    ]
