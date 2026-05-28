from odoo import models, fields
from odoo.tools import SQL


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    sales_man_id = fields.Many2one('res.partner', readonly=True)
    supervisor_id = fields.Many2one('res.partner', readonly=True)
    manager_id = fields.Many2one('res.partner', readonly=True)

    weight_received = fields.Float(readonly=True)
    weight_billed = fields.Float(readonly=True)

    def _select(self):
        return SQL("""
            %s,

            po.sales_man_id,
            po.supervisor_id,
            po.manager_id,

            SUM(
                COALESCE(p.weight, 0)
                * l.qty_received
                / NULLIF(u.factor, 0)
                * u2.factor
            ) AS weight_received,

            SUM(
                COALESCE(p.weight, 0)
                * l.qty_invoiced
                / NULLIF(u.factor, 0)
                * u2.factor
            ) AS weight_billed

        """, super()._select())

    def _group_by(self):
        return SQL("""
            %s,
            po.sales_man_id,
            po.supervisor_id,
            po.manager_id
        """, super()._group_by())
