# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


##################################### Account Move Class #####################################
class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    sales_man_id = fields.Many2one(
        'res.partner',
        string='Sales Man',
        domain=[('agent', '=', True)],
        tracking=True,
    )

    supervisor_id = fields.Many2one(
        'res.partner',
        string="Supervisor",
        domain=[('agent', '=', False)],
        tracking=True,
    )

    manager_id = fields.Many2one(
        'res.partner',
        string="Manager",
        tracking=True,
    )

    is_agent_required = fields.Boolean(
        string="Agent Required",
        related='company_id.is_agent_required',
        readonly=True,
    )

    @api.onchange('sales_man_id')
    def _onchange_sales_man_id(self):
        """
        Automatically set supervisor based on selected sales man.
        """
        for move in self:
            if move.sales_man_id and move.sales_man_id.supervisor_id:
                move.supervisor_id = move.sales_man_id.supervisor_id
            else:
                move.supervisor_id = False

    def action_register_payment(self):
        """
        Inject default values into payment register wizard context.
        """
        self.ensure_one()

        # Get standard Odoo action
        action = super().action_register_payment()

        if self.sales_man_id:

            # Ensure mutable dictionary
            context = dict(action.get('context', {}) or {})

            # Inject wizard default values
            context.update({
                'default_sales_man_id': self.sales_man_id.id,
                'default_supervisor_id': (
                    self.sales_man_id.supervisor_id.id
                    if self.sales_man_id.supervisor_id
                    else False
                ),
            })

            action['context'] = context

        return action
