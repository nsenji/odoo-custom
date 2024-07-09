{
    "name": "Custom purchases",
    "version": "1.0",
    "sequence": -100,
    "summary": "A customisation of the purchases module",
    "description": """
Custom Purchases
====================
This module customises the purchases module to add a few missing functionalities like the ability to assign RFQ to several vendors etc
    """,
    "category": "Purchase",
    "website": "",
    "depends": ["purchase", "mail"],
    "data": [
        "views/custom_purchase_order_views.xml",
        "data/custom_purchase_email_template.xml"
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "post_init_hook": "",
    "assets": {},
    "license": "LGPL-3",
}
