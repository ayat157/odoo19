from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # @api.constrains('product_uom_qty', 'product_id')
    def _check_available_qty(self):
        for line in self:
            if not line.product_id or line.product_id.type not in ['consu']:
                continue
            warehouse = line.order_id.warehouse_id
            stock_location = warehouse.lot_stock_id
            outgoing_moves = self.env['stock.move'].search([
                ('product_id', '=', line.product_id.id),
                ('location_id', '=', stock_location.id),
                ('state', 'in', ['confirmed', 'assigned', 'waiting', 'partially_available'])
            ])

            outgoing_qty = sum(outgoing_moves.mapped('product_uom_qty'))
            # Minus this order picking qty to get the past outgoing
            outgoing_qty = outgoing_qty - line.product_uom_qty

            quants = self.env['stock.quant'].search([
                ('product_id', '=', line.product_id.id),
                ('location_id', '=', stock_location.id),
            ])
            qty_on_hand = sum(quants.mapped('quantity'))

            qty_available = qty_on_hand - outgoing_qty

            if line.product_uom_qty > qty_available :
                raise ValidationError(_(
                    "The requested quantity (%s) for product: [%s] is not available in stock\n"
                    "On Hand Qty: [%s]\n"
                    "Outgoing Qty : [%s]\n"
                    "Available Qty : [%s] "
                ) % (
                                          line.product_uom_qty,
                                          line.product_id.display_name,
                                          qty_on_hand,
                                          outgoing_qty,
                                          qty_available,
                                      ))
