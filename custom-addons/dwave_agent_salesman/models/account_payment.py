# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    sales_man_id = fields.Many2one(
        'res.partner',
        string='Sales Man',
        domain=[('agent', '=', True)]
    )

    supervisor_id = fields.Many2one(
        "res.partner",
        string="Supervisor",
        domain=[('agent', '!=', True)]
    )

    is_agent_required = fields.Boolean(
        string="Agent Required",
        related='company_id.is_agent_required'
    )

    @api.onchange('sales_man_id')
    def _onchange_sales_man_id(self):
        for payment in self:
            payment.supervisor_id = payment.sales_man_id.supervisor_id.id
