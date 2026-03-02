from django.test import TestCase

from purchase_order.models import PurchaseOrder
from purchase_order.serializers import PurchaseOrderSerializer
from custom_user.models import User
from department.models import Department
from purchase_request.models import PurchaseRequest


# Create your tests here.


class PurchaseOrderSerializerTests(TestCase):
    def setUp(self):
        # common objects
        self.dept = Department.objects.create(name='DeptA')
        self.req_user = User.objects.create(username='req', dep_id=self.dept)
        self.po_user = User.objects.create(username='po_user')
        self.pr = PurchaseRequest.objects.create(
            title='PR1', description='req', requested_by=self.req_user
        )

    def test_department_fallback_from_pr(self):
        po = PurchaseOrder.objects.create(
            id=10,
            title='PO',
            description='d',
            requested_by_user=self.po_user,
            purchase_request=self.pr
        )
        data = PurchaseOrderSerializer(po).data
        self.assertEqual(data.get('department_id'), self.dept.id)
        self.assertEqual(data.get('department_name'), self.dept.name)

    def test_requester_fields(self):
        po = PurchaseOrder.objects.create(
            id=11,
            title='PO2',
            description='d2',
            requested_by_user=self.po_user,
        )
        data = PurchaseOrderSerializer(po).data
        # should fall back to requested_by_user since no purchase_request
        self.assertEqual(data.get('requester_id'), self.po_user.id)
        self.assertEqual(data.get('requester_username'), self.po_user.username)


class PurchaseOrderAPITests(TestCase):
    def setUp(self):
        self.client = self.client
        # reuse objects from serializer tests
        self.dept = Department.objects.create(name='DeptA')
        self.req_user = User.objects.create(username='req2', dep_id=self.dept)
        self.po_user = User.objects.create(username='po_user2', dep_id=self.dept)
        self.pr = PurchaseRequest.objects.create(
            title='PRx', description='req', requested_by=self.req_user
        )
        # create an order via purchase_request so department info comes from pr
        self.order = PurchaseOrder.objects.create(
            id=42,
            title='POx',
            description='desc',
            requested_by_user=self.po_user,
            purchase_request=self.pr,
            statuss='approved'  # need approved status to be returned by datatable view
        )

    def test_datatable_list_contains_computed_fields(self):
        url = '/datatable/po/list/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        results = body.get('results', [])
        self.assertTrue(any(r.get('id') == 42 for r in results))
        # pick our order
        item = next(r for r in results if r.get('id') == 42)
        self.assertEqual(item.get('department_id'), self.dept.id)
        self.assertEqual(item.get('department_name'), self.dept.name)
        # department map should also be present for legacy clients
        dept_map = item.get('department')
        self.assertIsInstance(dept_map, dict)
        self.assertEqual(dept_map.get('id'), self.dept.id)
        self.assertEqual(dept_map.get('name'), self.dept.name)
