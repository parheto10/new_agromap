# Generated by Django 3.2.7 on 2021-10-04 09:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0001_initial'),
        ('cooperatives', '0003_auto_20211002_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producteur',
            name='origine',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='producteurs', to='parametres.origine'),
        ),
    ]
