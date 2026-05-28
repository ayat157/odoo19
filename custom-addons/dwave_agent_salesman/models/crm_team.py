# -*- coding: utf-8 -*-
# Copyright 2024 WeDo Technology
# Website: http://wedotech-s.com
# Email: apps@wedotech-s.com
# Phone:00249900034328 - 00249122005009
# -*- coding: utf-8 -*-

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    restrict_zero_price = fields.Boolean(
        string='Restrict Zero Price'
    )

    restrict_zero_cost = fields.Boolean(
        string='Restrict Zero Cost'
    )

    restrict_unavailable_qty = fields.Boolean(
        string='Restrict Unavailable Qty'
    )
