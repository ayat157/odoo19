# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import UserError

class SalesmanStatementBase:
    
    def _get_report_data(self, docids, data=None):
        if not data or not data.get('form'):
            raise UserError(_("Form data not provided."))

        wizard = self.env['salesman.statement.wiz'].browse(docids)
        form = data['form']
        
        # Date Objects
        date_from = fields.Date.from_string(form['date_from'])
        date_to = fields.Date.from_string(form['date_to'])
        salesman_id = form['salesman_id'][0]
        
        # Currency Setup
        active_company = self.env.company
        company_currency = active_company.currency_id
        
        currency_id = form.get('currency_id') and form['currency_id'][0] or False
        target_currency = self.env['res.currency'].browse(currency_id) if currency_id else company_currency
        
        MoveLine = self.env['account.move.line']
        partners = self.env['res.partner'].search([
            ('agent_id', '=', salesman_id),
            ('customer_rank', '>', 0)
        ])

        if not partners:
             raise UserError(_("No customers found for the selected salesman."))

        lines = []
        grand_total = {
            'open_net': 0.0,
            'debit_move': 0.0, 
            'credit_move': 0.0,
            'end_net': 0.0,
        }

        for partner in partners:
            # 1. Get the Specific Account from Customer Profile
            receivable_account = partner.property_account_receivable_id
            
            # If for some reason it's missing, skip or fallback (usually always present)
            if not receivable_account:
                continue

            # 2. Base Domain: Use the specific 'account_id' instead of generic 'account_type'
            base_domain = [
                ('partner_id', '=', partner.id),
                ('account_id', '=', receivable_account.id),  # <--- EXACT ACCOUNT MATCH
                ('parent_state', '=', 'posted'),
                ('move_id.move_type', 'in', ['out_invoice', 'out_refund']) 
            ]

            # --- CALCULATE OPENING BALANCE ---
            balance_open = 0.0
            dom_open = base_domain + [('date', '<', date_from)]

            if target_currency == company_currency:
                # 1. Company Currency Report: Sum everything in Base Debit/Credit
                res = MoveLine.read_group(dom_open, ['debit', 'credit'], [])
                balance_open = (res[0]['debit'] or 0.0) - (res[0]['credit'] or 0.0)
            else:
                # 2. Foreign Currency Report: Split logic
                # A. Lines in Target Currency (Sum amount_currency)
                dom_same = dom_open + [('currency_id', '=', target_currency.id)]
                res_same = MoveLine.read_group(dom_same, ['amount_currency'], [])
                balance_open += res_same[0]['amount_currency'] or 0.0

                # B. Lines in Other Currency (Sum Base -> Convert)
                dom_diff = dom_open + [('currency_id', '!=', target_currency.id)]
                res_diff = MoveLine.read_group(dom_diff, ['debit', 'credit'], [])
                val_diff = (res_diff[0]['debit'] or 0.0) - (res_diff[0]['credit'] or 0.0)
                
                if abs(val_diff) > 0.0:
                    balance_open += company_currency._convert(
                        val_diff, target_currency, active_company, date_from
                    )

            # --- CALCULATE MOVEMENT ---
            debit_val = 0.0
            credit_val = 0.0
            dom_period = base_domain + [('date', '>=', date_from), ('date', '<=', date_to)]

            if target_currency == company_currency:
                # 1. Company Currency Report: Simple Sum of Debit/Credit columns
                res = MoveLine.read_group(dom_period, ['debit', 'credit'], [])
                debit_val = res[0]['debit'] or 0.0
                credit_val = res[0]['credit'] or 0.0
            else:
                # 2. Foreign Currency Report: Split logic
                
                # A. Lines in Target Currency
                # Debit Part (Positive amount_currency)
                dom_same_dr = dom_period + [('currency_id', '=', target_currency.id), ('amount_currency', '>', 0)]
                res_same_dr = MoveLine.read_group(dom_same_dr, ['amount_currency'], [])
                debit_val += res_same_dr[0]['amount_currency'] or 0.0

                # Credit Part (Negative amount_currency)
                dom_same_cr = dom_period + [('currency_id', '=', target_currency.id), ('amount_currency', '<', 0)]
                res_same_cr = MoveLine.read_group(dom_same_cr, ['amount_currency'], [])
                credit_val += abs(res_same_cr[0]['amount_currency'] or 0.0)

                # B. Lines in Other Currency (Convert Base Debits/Credits)
                dom_diff = dom_period + [('currency_id', '!=', target_currency.id)]
                res_diff = MoveLine.read_group(dom_diff, ['debit', 'credit'], [])
                
                val_diff_dr = res_diff[0]['debit'] or 0.0
                val_diff_cr = res_diff[0]['credit'] or 0.0

                if val_diff_dr > 0:
                    debit_val += company_currency._convert(val_diff_dr, target_currency, active_company, date_to)
                if val_diff_cr > 0:
                    credit_val += company_currency._convert(val_diff_cr, target_currency, active_company, date_to)

            # --- ENDING BALANCE ---
            balance_end = balance_open + debit_val - credit_val

            # --- PREPARE DATA ---
            line_data = {
                'partner_name': partner.name,
                'partner_code': partner.ref or partner.id, 
                'open_net': balance_open,       
                'debit_move': debit_val,   
                'credit_move': credit_val, 
                'end_net': balance_end,         
            }

            grand_total['open_net'] += balance_open
            grand_total['debit_move'] += debit_val
            grand_total['credit_move'] += credit_val
            grand_total['end_net'] += balance_end

            # Check if line has data
            has_data = (
                abs(balance_open) > 0.01 or 
                abs(debit_val) > 0.01 or 
                abs(credit_val) > 0.01
            )

            if has_data:
                lines.append(line_data)

        return {
            'doc_model': 'salesman.statement.wiz',
            'o': wizard,
            'data': data,
            'lines': lines,
            'totals': grand_total,
            'salesman': self.env['res.partner'].browse(salesman_id),
            'company': active_company,
            'currency': target_currency,
            'date_from': date_from,
            'date_to': date_to,
            'user': self.env.user,
        }