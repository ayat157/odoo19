from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

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

    manager_id = fields.Many2one(
        "res.partner",
        string="Manager"
    )

    is_agent_required = fields.Boolean(
        string="Agent Required",
        related='company_id.is_agent_required'
    )

    @api.onchange('partner_id')
    def _onchange_partner_id_set_sales_man(self):
        for order in self:
            order.sales_man_id = order.partner_id.agent_id if order.partner_id else False

    @api.onchange('sales_man_id')
    def _onchange_sales_man_id(self):
        for order in self:
            if order.sales_man_id:
                order.supervisor_id = order.sales_man_id.supervisor_id
                order.manager_id = order.sales_man_id.manager_id

                order.team_id = order.sales_man_id.team_id or order._default_team_id()

                if order.sales_man_id.warehouse_id:
                    order.warehouse_id = order.sales_man_id.warehouse_id

    def _default_team_id(self):
        return self.env['crm.team']._get_default_team_id()

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res.update({
            'sales_man_id': self.sales_man_id.id,
            'supervisor_id': self.supervisor_id.id,
        })
        return res

    @api.model
    def _cron_auto_invoice(self):
        orders = self.search([
            ('invoice_status', '=', 'to invoice'),
            ('state', '=', 'sale'),
        ])

        # فلترة آمنة بدل domain على team field
        orders = orders.filtered(lambda o: o.team_id.automated_create_invoice)

        for order in orders:
            order._create_invoices()

            if order.team_id.automated_validate_invoice:
                for inv in order.invoice_ids:
                    inv.action_post()

        return True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_procurement_values(self):
        values = super()._prepare_procurement_values()

        values.update({
            'sales_man_id': self.order_id.sales_man_id.id or False,
            'supervisor_id': self.order_id.supervisor_id.id or False,
        })

        return values
