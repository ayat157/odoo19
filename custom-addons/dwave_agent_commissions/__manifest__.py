# -*- coding: utf-8 -*-
{
    'name': "Dwave Agent Commissions",
    'summary': "Add Agent in Commissions",
    'description': "Add Agent in Commissions link it with Agent",
    'author': "Digital Waves Solutions",
    'website': "http://dwave-s.com",
    'category': 'Sales',
    'version': '19.0.0.2',
    'depends': ['dwave_agent_salesman', 'sale_commission'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_commission_add_multiple_agent.xml',
        'views/commission_plan_views.xml',
        'views/commission_agent_achievement_views.xml',
        'views/agent_commission_menu.xml',
    ],
}
