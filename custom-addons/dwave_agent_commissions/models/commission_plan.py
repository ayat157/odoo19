# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CommissionPlan(models.Model):
    _inherit = 'sale.commission.plan'

    agent_ids = fields.One2many('sale.commission.plan.agent', 'plan_id', copy=True)
    user_type = fields.Selection(
        selection_add=[('agent', "Agent")],
        ondelete={'agent': 'set default'},
    )

    def action_open_agent_commission(self):
        self.ensure_one()
        view_id = self.env.ref(
            'dwave_agent_commissions.sale_agent_commission_achievement_view_list',
            raise_if_not_found=False
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.agent.commission.achievement',
            'name': _("Agent Commissions"),
            'views': [[view_id.id if view_id else False, 'list'], [False, 'form']],
            'domain': [('agent_id', 'in', self.agent_ids.mapped('agent_id').ids)],
        }
