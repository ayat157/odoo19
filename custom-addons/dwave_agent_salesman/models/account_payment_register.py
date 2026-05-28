from odoo import models, fields


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    sales_man_id = fields.Many2one('res.partner', string="Sales Man")
    supervisor_id = fields.Many2one('res.partner', string="Supervisor")
