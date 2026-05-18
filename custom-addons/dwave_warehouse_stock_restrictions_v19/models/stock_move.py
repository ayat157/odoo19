# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.constrains('state', 'location_id', 'location_dest_id')
    def check_user_location_rights(self):

        for rec in self:

            # Skip draft/cancel/done
            if rec.state in ['draft', 'cancel', 'done']:
                continue

            user = self.env.user

            # Restriction disabled
            if not user.restrict_locations:
                continue

            # Internal transfers
            if rec.picking_type_id.code == 'internal':

                source_usage = rec.location_id.usage
                dest_usage = rec.location_dest_id.usage

                # Allow internal <-> transit
                if (
                    (source_usage == 'internal' and dest_usage == 'transit')
                    or
                    (source_usage == 'transit' and dest_usage == 'internal')
                ):
                    continue

            allowed_locations = user.stock_location_ids.ids

            # Check source
            if rec.location_id.id not in allowed_locations:
                raise UserError(_(
                    'You do not have access to source location: %s'
                ) % rec.location_id.display_name)

            # Check destination
            if rec.location_dest_id.id not in allowed_locations:
                raise UserError(_(
                    'You do not have access to destination location: %s'
                ) % rec.location_dest_id.display_name)
