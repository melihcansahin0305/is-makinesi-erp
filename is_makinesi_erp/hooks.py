app_name = "is_makinesi_erp"
app_title = "Is Makinesi ERP"
app_publisher = "Is Makinesi ERP"
app_description = "Is makinesi firmasi icin ERPNext uzerine insa edilmis kapsamli ERP cozumu. Makine yonetimi, puantaj, hakedis, yakit takibi, bakim, curuf isleme, skal uretimi ve satis modullerini icerir."
app_email = "info@ismakinesi.com"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]

# Modules
# ----------

modules = [
    {
        "module_name": "Is Makinesi ERP",
        "category": "Modules",
        "label": "Is Makinesi ERP",
        "color": "#2490ef",
        "icon": "octicon octicon-tools",
        "type": "module",
        "description": "Is makinesi yonetim sistemi",
    }
]

# Fixtures
# ----------
# Fixtures are used to export customizations and data from the site
# to the app directory. They can be imported back using bench import-fixtures.

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [["module", "=", "Is Makinesi ERP"]],
	},
]

# DocType Class Overrides
# ----------

# override_doctype_class = {
#     "Project": "is_makinesi_erp.overrides.project.CustomProject",
# }

# Dashboard Overrides
# ----------
override_doctype_dashboards = {
	"Customer": "is_makinesi_erp.overrides.customer_dashboard.get_data",
	"Project": "is_makinesi_erp.overrides.project_dashboard.get_data",
	"Employee": "is_makinesi_erp.overrides.employee_dashboard.get_data",
}

# Document Events
# ----------
# Hook on document methods and events.
# Placeholder for validation hooks on custom and ERPNext DocTypes.

doc_events = {
    "Project": {
        "on_update": "is_makinesi_erp.api.hesapla_proje_kar_zarar",
    },
}

# Scheduled Tasks
# ----------
# Scheduler events for automated notifications (Requirement 15).

scheduler_events = {
    "daily": [
        "is_makinesi_erp.tasks.check_bakim_bildirimi",
        "is_makinesi_erp.tasks.check_hakedis_vade_bildirimi",
        "is_makinesi_erp.tasks.check_eksik_puantaj_bildirimi",
    ],
    "daily_long": [
        "is_makinesi_erp.tasks.check_dusuk_stok_uyarisi",
    ],
}

# Jinja Environment
# ----------

# jinja = {
#     "methods": [],
#     "filters": [],
# }

# Installation
# ----------

# before_install = "is_makinesi_erp.install.before_install"
after_install = "is_makinesi_erp.install.after_install"

# Uninstallation
# ----------

# before_uninstall = "is_makinesi_erp.uninstall.before_uninstall"
# after_uninstall = "is_makinesi_erp.uninstall.after_uninstall"

# Website
# ----------

# website_generators = []

# Home Pages
# ----------

# home_page = "login"

# Desk Notifications
# ----------

# notification_config = "is_makinesi_erp.notifications.get_notification_config"

# Permissions
# ----------

# has_permission = {
#     "Event": "frappe.desk.doctype.event.event.has_permission",
# }

# User Data Protection
# ----------

# user_data_fields = [
#     {
#         "doctype": "{doctype_1}",
#         "filter_by": "{filter_by}",
#         "redact_fields": ["{field_1}", "{field_2}"],
#         "partial": 1,
#     },
# ]
