# Generated by Django 2.0.2 on 2018-03-16 18:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chesslogic', '0009_auto_20180316_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chesspiece',
            name='position',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chesslogic.ChessField', verbose_name='położenie na szachownicy'),
        ),
    ]