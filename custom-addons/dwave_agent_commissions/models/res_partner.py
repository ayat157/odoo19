# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    commission_plan_agent_ids = fields.One2many(
        'sale.commission.plan.agent', 'agent_id', 'Commission Plans'
    )
    filtered_commission_plan_agent_ids = fields.One2many(
        'sale.commission.plan.agent',
        compute='_compute_filtered_commission_plan_agent_ids'
    )

    @api.depends('commission_plan_agent_ids')
    def _compute_filtered_commission_plan_agent_ids(self):
        today = fields.Date.today()
        for partner in self:
            partner.filtered_commission_plan_agent_ids = \
                partner.commission_plan_agent_ids.filtered(
                    lambda x: (not x.date_from or x.date_from <= today) and
                              (not x.date_to or x.date_to >= today)
                )
