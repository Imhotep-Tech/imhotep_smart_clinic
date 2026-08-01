# Generated manually for prescription share link feature

import uuid
from django.db import migrations, models


def generate_unique_share_tokens(apps, schema_editor):
    MedicalRecord = apps.get_model('doctor', 'MedicalRecord')
    for record in MedicalRecord.objects.all():
        if not record.share_token:
            record.share_token = uuid.uuid4()
            record.save(update_fields=['share_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0003_clinic_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalrecord',
            name='share_token',
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
        migrations.RunPython(generate_unique_share_tokens, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
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
