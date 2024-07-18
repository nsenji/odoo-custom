{
    "name": "National Id Application",
    "version": "1.0",
    "sequence": -110,
    "summary": "A national ID application interface",
    "description": """
A national ID application platform
    """,
    "category": "National Id",
    
    "depends": ['base', 'mail', 'website'],
    "data": [
       'views/national_id_views.xml',
       'views/web_templates.xml',
       'security/ir.model.access.csv',
       'security/national_id_security.xml',
       'data/national_id_email_template.xml'
    ],
    
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
