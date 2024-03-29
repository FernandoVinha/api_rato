# Generated by Django 5.0.2 on 2024-03-03 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo_trap', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='phototrap',
            name='trap_status',
            field=models.CharField(choices=[('NONE', 'None'), ('T_REX_OK', 'T-Rex OK'), ('T_REX_DISARMED', 'T-Rex Disarmed'), ('GLUE_OK', 'Glue OK'), ('RAT_ON_GLUE', 'Rat on Glue'), ('GLUE_WITH_DUST', 'Glue with Dust'), ('POISON_OK', 'Poison OK'), ('LITTLE_POISON', 'Little Poison'), ('MOLDY_POISON', 'Moldy Poison')], default='NONE', max_length=20),
        ),
    ]
