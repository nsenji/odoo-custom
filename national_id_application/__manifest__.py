{
    "name": "National Id Application",
    "version": "1.0",
    "sequence": -110,
    "summary": "A national ID application interface",
    "description": """
A national ID application platform
    """,
    "category": "National Id",
    "website": "",
    "depends": ['base', 'mail', 'website'],
    "data": [
       'views/national_id_views.xml',
       'security/ir.model.access.csv',
       'security/national_id_security.xml',
       'data/national_id_email_template.xml'
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "post_init_hook": "",
    "assets": {},
    "license": "LGPL-3",
}
