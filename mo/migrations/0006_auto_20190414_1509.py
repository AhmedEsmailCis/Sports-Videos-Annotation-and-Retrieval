# Generated by Django 2.2 on 2019-04-14 13:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mo', '0005_auto_20190414_1505'),
    ]

    operations = [
        migrations.DeleteModel(
            name='em',
        ),
        migrations.RenameField(
            model_name='video',
            old_name='cat_name',
            new_name='cat_id',
        ),
        migrations.AlterField(
            model_name='video',
            name='cat_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mo.category'),
        ),
    ]