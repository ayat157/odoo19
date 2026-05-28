# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SalesmanStatementWizard(models.TransientModel):
    _name = 'salesman.statement.wiz'
    _description = 'Salesman Customer Statement Wizard'

    date_from = fields.Date(
        string='From Date', 
        required=True, 
        default=lambda self: fields.Date.today().replace(day=1, month=1)
    )
    date_to = fields.Date(
        string='To Date', 
        required=True, 
        default=fields.Date.today
    )
    salesman_id = fields.Many2one(
        'res.partner', 
        string='Salesman (المندوب)',
        required=True,
        domain="[('agent', '=', True)]" 
    )
    # 1. Added Currency Option
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency (Optional)",
        help="Select a currency to filter and calculate amounts. Leave empty for Company Currency."
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company
    )

    def print_report(self):
        """
        Called by the 'Print' button.
        This function checks the user's language and returns
        the correct report action (EN or AR).
        """
        data = {
            'form': self.read()[0],
        }
        
        # Check the user's language
        if self.env.user.lang and self.env.user.lang.startswith('ar'):
            # If Arabic, call the Arabic report action
            report_action_ref = 'dwave_agent_salesman.action_report_salesman_statement_ar'
        else:
            # Default to English
            report_action_ref = 'dwave_agent_salesman.action_report_salesman_statement_en'
        
        # Return the correct report
        return self.env.ref(report_action_ref).report_action(self, data=data)