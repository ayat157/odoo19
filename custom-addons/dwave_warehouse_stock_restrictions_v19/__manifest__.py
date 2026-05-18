   # -*- coding: utf-8 -*-
{
    'name': "Warehouse Restrictions (Odoo 19 Compatible)",

    'summary': "Restrict warehouse and stock locations per user",

    'description': """
        This module allows restricting users to specific warehouses and
        controlling access to stock operations based on allowed warehouses.
    """,

    'author': "Techspawn Solutions (Refactored)",
    'website': "http://www.techspawn.com",

    'license': 'OPL-1',
    'category': 'Inventory',
    'version': '19.0.1.0.0',

    'depends': [
        'base',
        'stock',
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/users_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
