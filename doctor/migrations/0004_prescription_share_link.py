# Generated manually for prescription share link feature

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0003_clinic_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalrecord',
            name='share_token',
            field=models.UUIDField(blank=True, default=uuid.uuid4, editable=False, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='is_shareable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='share_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
