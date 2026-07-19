from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime, time

class ImexInventoryWizard(models.TransientModel):
    _name = "imex.inventory.wizard"
    _description = "Inventory Report Wizard"

    date_from = fields.Date(required=True, default=lambda self: date.today())
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    location_id = fields.Many2one(
        "stock.location",
        required=True,
        domain=[('usage', '=', 'internal')]
    )
    barcode = fields.Char(string="Scan Barcode")
    product_ids = fields.Many2many("product.product")
    product_category_ids = fields.Many2many("product.category")
    weight_in_ton = fields.Boolean('Show Weight In Ton?', defailt=False)
    report_type = fields.Selection(
        [
            ('raw_materials', 'Raw Materials'),
            ('assets', 'Assets'),
        ],
        string="Report Type",
        default='raw_materials',
        required=True,
    )

    @api.onchange('barcode')
    def _onchange_barcode(self):
        if not self.barcode:
            return

        if self.report_type != 'assets':
            product = self.env['product.product'].search(
                [('barcode', '=', self.barcode)],
                limit=1
            )

            if not product:
                raise UserError("No product found for this barcode.")

            self.product_ids = [(4, product.id)]
            self.barcode = False  # clear for next scan
        
    def action_view_report(self):
        self.ensure_one()

        if self.date_from > self.date_to:
            raise UserError("Date From cannot be after Date To.")

        # Clear previous report data
        self.env['imex.inventory.report'].search([]).unlink()

        # Get location and child locations
        location_ids = self.env['stock.location'].search([('id', 'child_of', self.location_id.id)]).ids
        if not location_ids:
            raise UserError("No internal locations found.")

        # Get product IDs to report on
        product_ids = self.product_ids.ids if self.product_ids else self.env['product.product'].search([('type', '=', 'consu')]).ids
        
        if self.product_category_ids:
            product_ids = self.env['product.product'].search([
                ('type', '=', 'consu'),
                ('categ_id', 'child_of', self.product_category_ids.ids)
            ]).ids

        if not product_ids:
            raise UserError("No products found with selected filters.")

        # Calculate quantities and prepare data
        date_from_dt = datetime.strptime(str(self.date_from), '%Y-%m-%d')
        date_to_dt = datetime.strptime(str(self.date_to), '%Y-%m-%d')
        period_start = datetime.combine(date_from_dt.date(), time.min)
        period_end = datetime.combine(date_to_dt.date(), time.max)
        # period_end_next = datetime.combine(date_to_dt.date(), time.min) + timedelta(days=1)
        period_end_next = datetime.combine(date_to_dt.date(), time.max)
        weight_in_ton = self.weight_in_ton
        ton_uom = self.env.ref('uom.product_uom_ton')

        product_recs = self.env['product.product'].browse(product_ids)
        
        # Context for quantity calculations
        initial_ctx = {
            'location': self.location_id.id,
            'compute_child': True,
            'to_date': period_start.strftime('%Y-%m-%d %H:%M:%S'),
        }
        closing_ctx = {
            'location': self.location_id.id,
            'compute_child': True,
            'to_date': period_end_next.strftime('%Y-%m-%d %H:%M:%S'),
        }

        # Calculate move in/out from SQL
        cr = self.env.cr
        cr.execute("""
            SELECT
                pp.id AS product_id,
                COALESCE(SUM(
                    CASE
                        WHEN sm.date >= %(period_start)s
                             AND sm.date <= %(period_end_next)s
                             AND sml.location_dest_id IN %(location_ids)s
                             AND sml.location_id NOT IN %(location_ids)s
                        THEN sml.quantity
                        ELSE 0
                    END
                ), 0) AS product_in,
                COALESCE(SUM(
                    CASE
                        WHEN sm.date >= %(period_start)s
                             AND sm.date <= %(period_end_next)s
                             AND sml.location_id IN %(location_ids)s
                             AND sml.location_dest_id NOT IN %(location_ids)s
                        THEN sml.quantity
                        ELSE 0
                    END
                ), 0) AS product_out
            FROM product_product pp
            LEFT JOIN stock_move_line sml ON sml.product_id = pp.id
            LEFT JOIN stock_move sm ON sm.id = sml.move_id AND sm.state = 'done'
            WHERE pp.id IN %(product_ids)s
            GROUP BY pp.id
        """, {
            'period_start': period_start,
            'period_end_next': period_end_next,
            'location_ids': tuple(location_ids),
            'product_ids': tuple(product_ids),
        })

        move_result = {row[0]: (row[1], row[2]) for row in cr.fetchall()}

        # Create report rows
        rows_data = []
        view_id = self.env.ref(
            'dwave_inventory_report.view_imex_inventory_report_list'
        ).id 
        initial_weight_ton = product_in_weight_ton = product_out_weight_ton = \
        balance_weight_ton = virtual_available_weight_ton = 0.0
            
        for product in product_recs:
            initial = product.with_context(**initial_ctx).qty_available
            balance = product.with_context(**closing_ctx).qty_available
            virtual_available = product.with_context(**closing_ctx).free_qty
            qty_available = product.with_context(**closing_ctx).qty_available
            product_in, product_out = move_result.get(product.id, (0.0, 0.0))

            if weight_in_ton:
                initial_weight_ton = (product.weight * initial) / 1000 if product.weight > 0.0 else 0.0
                product_in_weight_ton = (product.weight * product_in) / 1000 if product.weight > 0.0 else 0.0
                product_out_weight_ton = (product.weight * product_out) / 1000 if product.weight > 0.0 else 0.0
                balance_weight_ton = (product.weight * balance) / 1000 if product.weight > 0.0 else 0.0
                virtual_available_weight_ton = (product.weight * virtual_available) / 1000 if product.weight > 0.0 else 0.0

            rows_data.append({
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'product_category': product.categ_id.id,
                'location': self.location_id.id,
                'initial': initial,
                'product_in': product_in,
                'product_out': product_out,
                'balance': balance,
                'virtual_available': virtual_available,
                #'virtual_available': qty_available,
                
                'initial_weight_ton': initial_weight_ton,
                'product_in_weight_ton': product_in_weight_ton,
                'product_out_weight_ton': product_out_weight_ton,
                'balance_weight_ton': balance_weight_ton,
                'virtual_available_weight_ton': virtual_available_weight_ton,
    
                'total_value': balance * product.standard_price,
                'weight_in_ton': weight_in_ton,
            })

        if rows_data:
            self.env['imex.inventory.report'].create(rows_data)

        # Return action
        domain = [('location', '=', self.location_id.id)]
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))
        if self.product_category_ids:
            domain.append(('product_category', 'in', self.product_category_ids.ids))

        if weight_in_ton:
            view_id = self.env.ref(
                'dwave_inventory_report.view_imex_inventory_weight_ton_report_list'
            ).id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventory Summary',
            'res_model': 'imex.inventory.report',
            'view_mode': 'list,kanban',
            'views': [(view_id, 'list')],
            'domain': domain,
            'target': 'current',
        }

    def action_view_asset(self):
        self.ensure_one()

        asset = self.env['account.asset.assign'].search(
            [('barcode', '=', self.barcode)]
        )

        if not asset:
            raise UserError("No asset found for this barcode.")

        if len(asset) > 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Assets',
                'res_model': 'account.asset.assign',
                'view_mode': 'list,form',
                'domain': [('id', 'in', asset.ids)],
            }
            
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asset',
            'res_model': 'account.asset.assign',
            'view_mode': 'form',
            'res_id': asset.id,
            'target': 'current',
        }


    
