import uuid
from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

from doctor.models import Clinic, DoctorProfile, Patients, MedicalRecord

User = get_user_model()

class PrescriptionShareLinkTests(TestCase):
    def setUp(self):
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            email='doctor1@example.com',
            password='password123',
            is_doctor=True
        )
        self.doctor_profile = DoctorProfile.get_or_create_for_user(self.doctor_user)
        
        self.other_doctor_user = User.objects.create_user(
            username='doctor2',
            email='doctor2@example.com',
            password='password123',
            is_doctor=True
        )
        self.other_doctor_profile = DoctorProfile.get_or_create_for_user(self.other_doctor_user)

        self.patient = Patients.objects.create(
            doctor=self.doctor_profile,
            name='John Doe',
            phone_number='123456789',
            gender='Male'
        )

        self.medical_record = MedicalRecord.objects.create(
            doctor=self.doctor_profile,
            patient=self.patient,
            details='<p>Clinical notes</p>',
            prescription='<p>Take 1 tablet daily</p>'
        )

        self.client = Client()

    def test_default_share_link_state(self):
        self.assertFalse(self.medical_record.is_shareable)
        self.assertIsNone(self.medical_record.share_expires_at)
        self.assertFalse(self.medical_record.is_share_link_active())

    def test_share_link_active_status(self):
        self.medical_record.is_shareable = True
        self.medical_record.share_expires_at = None
        self.assertTrue(self.medical_record.is_share_link_active())

        # Future expiration date
        self.medical_record.share_expires_at = timezone.now() + timedelta(days=2)
        self.assertTrue(self.medical_record.is_share_link_active())

        # Past expiration date
        self.medical_record.share_expires_at = timezone.now() - timedelta(days=1)
        self.assertFalse(self.medical_record.is_share_link_active())

    def test_toggle_prescription_share_api(self):
        self.client.login(username='doctor1', password='password123')
        url = reverse('toggle_prescription_share', kwargs={'record_id': self.medical_record.id})

        # Enable link with future expiration
        future_iso = (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M')
        response = self.client.post(url, {
            'action': 'enable',
            'expires_at': future_iso
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['is_shareable'])

        self.medical_record.refresh_from_db()
        self.assertTrue(self.medical_record.is_shareable)
        self.assertIsNotNone(self.medical_record.share_expires_at)

        # Disable link
        response = self.client.post(url, {'action': 'disable'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['is_shareable'])

        self.medical_record.refresh_from_db()
        self.assertFalse(self.medical_record.is_shareable)
        self.assertIsNone(self.medical_record.share_expires_at)

    def test_public_access_when_disabled_or_expired(self):
        token = self.medical_record.share_token or uuid.uuid4()
        self.medical_record.share_token = token
        self.medical_record.is_shareable = False
        self.medical_record.save()

        public_url = reverse('shared_prescription_pdf', kwargs={'token': token})
        
        # Access disabled link (unauthenticated client)
        response = self.client.get(public_url)
        self.assertEqual(response.status_code, 403)
        self.assertIn('This prescription share link is no longer shared or has expired.', response.content.decode('utf-8'))
        self.assertIn('10', response.content.decode('utf-8')) # 10s countdown

        # Access expired link
        self.medical_record.is_shareable = True
        self.medical_record.share_expires_at = timezone.now() - timedelta(hours=1)
        self.medical_record.save()

        response = self.client.get(public_url)
        self.assertEqual(response.status_code, 403)
        self.assertIn('This prescription share link is no longer shared or has expired.', response.content.decode('utf-8'))

    def test_unauthorized_doctor_cannot_toggle_other_doctor_record(self):
        self.client.login(username='doctor2', password='password123')
        url = reverse('toggle_prescription_share', kwargs={'record_id': self.medical_record.id})

        response = self.client.post(url, {'action': 'enable'})
        self.assertEqual(response.status_code, 404)
