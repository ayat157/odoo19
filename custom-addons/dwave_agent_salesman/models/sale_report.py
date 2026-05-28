from odoo import models, fields, _

class SaleReport(models.Model):
    _inherit = "sale.report"

    sales_man_id = fields.Many2one('res.partner', 'Sales Man', readonly=True)
    supervisor_id = fields.Many2one('res.partner', 'Supervisor', readonly=True)
    manager_id = fields.Many2one('res.partner', 'Manager', readonly=True)

    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True)
    weight_delivered = fields.Float(string='Weight Delivered', readonly=True)
    weight_invoiced = fields.Float(string='Weight Invoiced', readonly=True)

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
    def _from_sale(self):
        from_clause = super()._from_sale()
        from_clause += """
        LEFT JOIN uom_uom u_sale ON (l.product_uom_id = u_sale.id)
        LEFT JOIN uom_uom u_sale2 ON (t.uom_id = u_sale2.id)
        """
        return from_clause

    def _group_by_sale(self):
        group_by_ = super()._group_by_sale()
        group_by_ += ", s.sales_man_id, s.supervisor_id, s.manager_id, s.payment_term_id"
        return group_by_
