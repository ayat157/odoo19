from odoo import models, fields, api
from odoo.exceptions import UserError

class ImexInventoryReport(models.Model):
    _name = "imex.inventory.report"
    _description = "Inventory Summary Report"
    _order = "product_id"

    product_id = fields.Many2one("product.product", readonly=True)
    product_uom = fields.Many2one("uom.uom", readonly=True)
    product_category = fields.Many2one("product.category", readonly=True)
    location = fields.Many2one("stock.location", readonly=True)
    standard_price = fields.Float("Unit Cost", related="product_id.standard_price", readonly=True)
    total_value = fields.Float("Total Value", readonly=True, group_operator="sum")

    initial = fields.Float("Initial", readonly=True, group_operator="sum", store=True)
    product_in = fields.Float("Product In", readonly=True, group_operator="sum", store=True)
    product_out = fields.Float("Product Out", readonly=True, group_operator="sum", store=True)
    balance = fields.Float("Balance", readonly=True, store=True, group_operator="sum")
    virtual_available = fields.Float("Available Qty", readonly=True, group_operator="sum", store=True)
    weight_in_ton = fields.Boolean('Show Weight In Ton?', defailt=False, store=True)

    initial_weight_ton = fields.Float(
        string="Initial (Ton)",
        readonly=True,
        group_operator="sum", store=True
    )
    product_in_weight_ton = fields.Float(
        string="Product In (Ton)",
        readonly=True,
        group_operator="sum", store=True
    )
    product_out_weight_ton = fields.Float(
        string="Product Out (Ton)",
        readonly=True,
        group_operator="sum", store=True
    )
    balance_weight_ton = fields.Float(
        string="Balance (Ton)",
        readonly=True,
        group_operator="sum", store=True
    )
    virtual_available_weight_ton = fields.Float(
        string="Available Qty (Ton)",
        readonly=True,
        group_operator="sum", store=True
    )


    def action_open_product(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Product',
            'res_model': 'product.product',
            'view_mode': 'form',
            'res_id': self.product_id.id,
            'target': 'current',
        }

    def action_view_move_history(self):
        self.ensure_one()

        ctx = self.env.context
        date_from = ctx.get('date_from')
        date_to = ctx.get('date_to')

        if not date_from or not date_to:
            raise UserError("Date range is missing. Please open the report from the wizard.")

        domain = [
            ('state', '=', 'done'),
            ('product_id', '=', self.product_id.id),
            '|',
            ('location_id', '=', self.location.id),
            ('location_dest_id', '=', self.location.id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Move History',
            'res_model': 'stock.move.line',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }


