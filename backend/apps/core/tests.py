from django.test import TestCase
from django.urls import reverse

from apps.core.models import LabRequest, Patient


class RequestCreateViewTests(TestCase):
    def test_dashboard_renders(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recent Lab Requests")

    def test_post_creates_patient_and_lab_request(self):
        response = self.client.post(
            reverse("request_create"),
            {
                "patient_full_name": "Juan Dela Cruz",
                "patient_sex": "male",
                "patient_birth_date": "1990-03-10",
                "age_snapshot_text": "",
                "request_datetime": "2026-03-10T09:30",
                "case_number": "CASE-001",
                "notes": "Walk-in patient",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(LabRequest.objects.count(), 1)

        patient = Patient.objects.get()
        lab_request = LabRequest.objects.get()

        self.assertEqual(patient.full_name, "Juan Dela Cruz")
        self.assertEqual(lab_request.patient, patient)
        self.assertEqual(lab_request.patient_name_snapshot, "Juan Dela Cruz")
        self.assertEqual(lab_request.case_number, "CASE-001")
        self.assertTrue(lab_request.request_no.startswith("REQ-"))
