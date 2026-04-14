from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from custom_user.models import User
from .models import Supplier, SupplierStat


class SupplierRecommendationAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.approved_supplier = Supplier.objects.create(
            name='Approved Supplier',
            contact_email='approved@example.com',
            approval_status='approved'
        )
        self.rejected_supplier = Supplier.objects.create(
            name='Rejected Supplier',
            contact_email='rejected@example.com',
            approval_status='rejected'
        )

        SupplierStat.objects.create(
            supplier=self.approved_supplier,
            date=date.today(),
            total_spend=1500.00,
            orders_count=3,
            avg_order=500.00
        )

    def test_recommendations_returns_approved_supplier(self):
        response = self.client.get('/supplier/supplier/recommendations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Approved Supplier')
        self.assertEqual(response.data[0]['approval_status'], 'approved')
        self.assertIn('total_spend', response.data[0])
        self.assertIn('score', response.data[0])

    def test_recommendations_top_parameter_limits_results(self):
        Supplier.objects.create(
            name='Another Approved Supplier',
            contact_email='another@example.com',
            approval_status='approved'
        )

        response = self.client.get('/supplier/supplier/recommendations/?top=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_recommendations_similar_supplier(self):
        other_supplier = Supplier.objects.create(
            name='Other Approved Supplier',
            contact_email='other@example.com',
            approval_status='approved'
        )
        SupplierStat.objects.create(
            supplier=other_supplier,
            date=date.today(),
            total_spend=1400.00,
            orders_count=2,
            avg_order=700.00
        )

        response = self.client.get(f'/supplier/supplier/recommendations/?supplier_id={self.approved_supplier.id}&top=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Other Approved Supplier')