from odoo import fields, models
from odoo.tools import SQL


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    sales_man_id = fields.Many2one('res.partner', string='Sales Man', readonly=True)
    supervisor_id = fields.Many2one('res.partner', string='Supervisor', readonly=True)
    manager_id = fields.Many2one('res.partner', string='Manager', readonly=True)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True)
    weight_received = fields.Float(string='Weight Received', readonly=True)
    weight_billed = fields.Float(string='Weight Billed', readonly=True)

    def _select(self):
        return SQL("""
            %s,
            po.sales_man_id,
            po.supervisor_id,
            po.manager_id,
            po.payment_term_id,
            SUM(p.weight * l.qty_received / NULLIF(u.factor, 0) * u2.factor) AS weight_received,
            SUM(p.weight * l.qty_invoiced / NULLIF(u.factor, 0) * u2.factor) AS weight_billed
        """, super()._select())

    def _from(self):
        return SQL("""
            %s
            LEFT JOIN uom_uom u ON (l.product_uom_id = u.id)
            LEFT JOIN uom_uom u2 ON (t.uom_id = u2.id)
        """, super()._from())

    def _group_by(self):
        return SQL(
            "%s, po.sales_man_id, po.supervisor_id, po.manager_id, po.payment_term_id",
            super()._group_by(),
        )
