from odoo import models, fields, api


class StockReference(models.Model):
    _inherit = 'stock.reference'

    sales_man_id = fields.Many2one('res.partner', string='Sales Man')
    supervisor_id = fields.Many2one('res.partner', string='Supervisor')


class StockPicking(models.Model):
    _inherit = "stock.picking"

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
        for rec in self:
            if rec.sales_man_id:
                rec.supervisor_id = rec.sales_man_id.supervisor_id


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        vals = super()._get_new_picking_values()

        if self.reference_ids:
            ref = self.reference_ids[0]
            vals.update({
                'sales_man_id': ref.sales_man_id.id or False,
                'supervisor_id': ref.supervisor_id.id or False,
            })

        return vals
