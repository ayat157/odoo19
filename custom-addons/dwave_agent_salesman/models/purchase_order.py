from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sales_man_id = fields.Many2one('res.partner')
    supervisor_id = fields.Many2one('res.partner')
    manager_id = fields.Many2one('res.partner')
    # payment_term_id is already in purchase.order, so we don't need to redefine it
