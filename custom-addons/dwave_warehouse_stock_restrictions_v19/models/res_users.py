# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean(
        string='Restrict Location',
        default=False,
    )

    stock_location_ids = fields.Many2many(
        comodel_name='stock.location',
        relation='location_security_stock_location_users',
        column1='user_id',
        column2='location_id',
        string='Stock Locations',
    )

    default_picking_type_ids = fields.Many2many(
        comodel_name='stock.picking.type',
        relation='stock_picking_type_users_rel',
        column1='user_id',
        column2='picking_type_id',
        string='Default Warehouse Operations',
    )
