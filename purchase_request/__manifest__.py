{
    "name": "Purchase Request",
    "version": "1.0",
    "sequence": -120,
    "summary": "A module for requesting purchases",
    "description": """
A module for requesting purhcases
    """,
    "category": "Purchase Request",
    
    "depends": ['base', 'mail', 'purchase'],
    "data": [
        'security/ir.model.access.csv',
        'views/purchase_request_views.xml'
    ],
    
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
