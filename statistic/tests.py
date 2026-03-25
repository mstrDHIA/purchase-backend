from django.test import TestCase, RequestFactory
from statistic import views
from purchase_order.models import PurchaseOrder
from custom_user.models import User as CustomUser
from department.models import Department


class GetFilteredPurchaseOrdersTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # create a department and users
        self.dept = Department.objects.create(name="Dept1")
        self.user_with_dept = CustomUser.objects.create(username="u1", dep_id=self.dept)
        self.user_without_dept = CustomUser.objects.create(username="u2")
        # purchase orders (must specify mandatory fields)
        self.po1 = PurchaseOrder.objects.create(
            id=1,
            title='PO1',
            description='first',
            requested_by_user=self.user_with_dept
        )
        self.po2 = PurchaseOrder.objects.create(
            id=2,
            title='PO2',
            description='second',
            requested_by_user=self.user_without_dept
        )

    def make_request(self, params=None):
        params = params or {}
        request = self.factory.get('/fake-url/', params)
        return request

    def test_always_excludes_null_dept(self):
        req = self.make_request()
        # disable built-in status filter for test simplicity
        qs = views.get_filtered_purchase_orders(req, include_status_filter=False)
        # should not contain po2 because it lacks a department
        ids = {po.id for po in qs}
        self.assertIn(self.po1.id, ids)
        self.assertNotIn(self.po2.id, ids)

    def test_filters_still_apply(self):
        # double-check other filters unaffected
        req = self.make_request({'department': str(self.dept.id)})
        qs = views.get_filtered_purchase_orders(req, include_status_filter=False)
        ids = {po.id for po in qs}
        self.assertEqual(ids, {self.po1.id})
