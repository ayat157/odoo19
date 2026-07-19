from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    block_decimal_mo_qty = fields.Boolean(string="Block decimal MO Qty")
    module_base_tier_validation_formula = fields.Boolean(string="Tier Formula")

    def get_values(self):
        res = super().get_values()
        IrConfigParam = self.env["ir.config_parameter"].sudo()

        res.update({
            "block_decimal_mo_qty": IrConfigParam.get_param(
                "base_tier_validation.block_decimal_mo_qty",
                default="False"
            ) == "True",
        })

        return res

    def set_values(self):
        super().set_values()
        IrConfigParam = self.env["ir.config_parameter"].sudo()

        IrConfigParam.set_param(
            "base_tier_validation.block_decimal_mo_qty",
            str(self.block_decimal_mo_qty)
        )