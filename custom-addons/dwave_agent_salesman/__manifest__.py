# -*- coding: utf-8 -*-
{
    'name': "Dwave Agent Slaesman",
    'summary': """ Add Sale Man in Sale & Invoice & Payment """,
    'description': """ Add Sale Man in Sale & Invoice & Payment link it with Employee""",
    'author': "Digital Waves Solutions",
    'website': "http://dwave-s.com",
    'category': 'Sales',
    'version': '19.0.0.1',
    'depends': ['sale_stock', 'account', 'stock', 'crm', 'sales_team', 'purchase'],
    'data': [
        'views/res_partner_view.xml',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
        'views/sale_order_view.xml',
        'views/stock_picking_view.xml',
        'views/crm_team_view.xml',
        'views/res_config_settings_views.xml',
        'views/report_picking_inherit_salesman.xml',
        'views/sale_report_view.xml',
        'views/purchase_report_view.xml',
        'views/account_invoice_report_view.xml',
        'wizards/agent_invoices_wiz.xml', # Kept
        'reports/agent_invoices.xml', # Kept
        'security/ir.model.access.csv', # Kept and updated below
        'reports/stock_picking_inherit.xml',
	    'reports/salesman_statement.xml',
        'wizards/salesman_statement_wiz.xml',
        'data/cron.xml',


    ],

    'license': 'LGPL-3',
    'installable': True,
    
}   
