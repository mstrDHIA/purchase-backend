"""Empty migration placeholder to fix malformed previous migration file.

If you intended to add a supplier ForeignKey to `PurchaseOrder`, update
the model and run `makemigrations` to create a proper migration.
"""
from django.db import migrations


class Migration(migrations.Migration):

	dependencies = [
		('purchase_order', '0010_purchaseorder_statuss'),
	]

	operations = [
		# intentionally left empty
	]

