# Generated by Django 2.2 on 2019-04-14 13:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mo', '0007_auto_20190414_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='cat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mo.category'),
        ),
    ]