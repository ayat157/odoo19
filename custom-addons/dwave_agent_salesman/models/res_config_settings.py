from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_agent_required = fields.Boolean(
        string="Agent Required",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_agent_required = fields.Boolean(
        string="Agent Required",
        related='company_id.is_agent_required',
        readonly=False,
    )
