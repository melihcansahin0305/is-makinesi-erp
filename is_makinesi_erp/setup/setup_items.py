import frappe
from frappe import _


SKAL_ITEMS = [
	{
		"item_code": "INCE-SKAL",
		"item_name": "İnce Skal",
		"item_group": "Products",
		"stock_uom": "Kg",
		"is_stock_item": 1,
		"description": "Cüruf işleme sonucu elde edilen ince skal ürünü",
	},
	{
		"item_code": "YAPRAK-SKAL",
		"item_name": "Yaprak Skal",
		"item_group": "Products",
		"stock_uom": "Kg",
		"is_stock_item": 1,
		"description": "Cüruf işleme sonucu elde edilen yaprak skal ürünü",
	},
	{
		"item_code": "KABA-SKAL",
		"item_name": "Kaba Skal",
		"item_group": "Products",
		"stock_uom": "Kg",
		"is_stock_item": 1,
		"description": "Cüruf işleme sonucu elde edilen kaba skal ürünü",
	},
]

DEFAULT_WAREHOUSE = "Skal Deposu - IME"


def create_skal_items():
	"""Skal ürünlerini ERPNext Item olarak oluşturur ve varsayılan depoyu tanımlar."""
	_create_warehouse()
	_create_items()


def _create_warehouse():
	"""Skal Deposu warehouse'unu oluşturur (yoksa). Company tanımlı değilse atlar."""
	company = frappe.defaults.get_defaults().get("company")
	if not company:
		# ERPNext setup wizard henüz tamamlanmamış, warehouse sonra oluşturulacak
		return
	if not frappe.db.exists("Warehouse", DEFAULT_WAREHOUSE):
		warehouse = frappe.get_doc(
			{
				"doctype": "Warehouse",
				"warehouse_name": "Skal Deposu",
				"company": company,
			}
		)
		warehouse.insert(ignore_permissions=True)
		frappe.db.commit()




def _ensure_item_group():
	"""Products Item Group yoksa oluşturur."""
	if not frappe.db.exists("Item Group", "Products"):
		parent = "All Item Groups" if frappe.db.exists("Item Group", "All Item Groups") else ""
		doc = frappe.get_doc({
			"doctype": "Item Group",
			"item_group_name": "Products",
			"parent_item_group": parent,
		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()


def _ensure_uom():
	"""Kg UOM yoksa oluşturur."""
	if not frappe.db.exists("UOM", "Kg"):
		doc = frappe.get_doc({
			"doctype": "UOM",
			"uom_name": "Kg",
		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()


def _create_items():
	"""Skal Item kayıtlarını oluşturur (yoksa). Gerekli bağımlılıkları kontrol eder."""
	_ensure_item_group()
	_ensure_uom()

	for item_data in SKAL_ITEMS:
		if not frappe.db.exists("Item", item_data["item_code"]):
			item = frappe.get_doc(
				{
					"doctype": "Item",
					**item_data,
				}
			)
			item.insert(ignore_permissions=True)

	frappe.db.commit()


