# -*- coding: utf-8 -*-
{
    'name': "Sale Order Approval",
    'summary': "Require manager approval for high-value sale orders before confirmation.",
    'description': """
This module enforces an approval process for sale orders that exceed a configurable threshold amount.
Key Features:
- Add approval workflow for high-value sale orders
- Configurable approval amount in system settings
- Seamless integration with Sales and Inventory
    """,
    'author': "Shibili",
    'category': 'Sales',
    'version': '1.0.0',
    'license': 'LGPL-3',
    'depends': ['base', 'sale_management', 'stock'],
    'data': [
        'security/security.xml',
        'views/res_config_setting.xml',
        'views/sale.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install':False,
}