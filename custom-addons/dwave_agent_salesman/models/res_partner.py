from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    warehouse_id = fields.Many2one('stock.warehouse', string='Default Warehouse')

    agent = fields.Boolean(string="Is Agent")

    agent_id = fields.Many2one(
        'res.partner',
        string="Agent",
        domain=[('agent', '=', True)],
    )

    supervisor_id = fields.Many2one(
        "res.partner",
        string="Supervisor",
        domain=[('agent', '=', False)],
    )

    manager_id = fields.Many2one(
        "res.partner",
        string='Manager',
        domain=[('agent', '=', True)],
    )

    team_id = fields.Many2one("crm.team", string="Sales Team")

    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        domain = args

        if name:
            domain = expression.AND([
                ['|', ('name', operator, name), ('phone', operator, name)],
                args
            ])

        records = self.search_fetch(domain, ['name', 'phone'], limit=limit)
        return [(r.id, r.display_name) for r in records]
