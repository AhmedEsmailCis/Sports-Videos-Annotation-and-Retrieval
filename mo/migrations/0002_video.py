# Generated by Django 2.2 on 2019-04-14 12:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('admin_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('cat_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mo.Category')),
            ],
        ),
    ]
