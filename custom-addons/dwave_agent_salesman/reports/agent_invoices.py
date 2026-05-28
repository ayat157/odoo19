from odoo import api, fields, models, _
from operator import itemgetter
import operator
from odoo.exceptions import UserError, ValidationError

class AgentInvoices(models.AbstractModel):
    # BUG FIX: changed module prefix to 'dwave_agent_salesman'
    _name = 'report.dwave_agent_salesman.report_agent_invoices_template'
    _description = 'Agent Invoices Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):

        dat = data['form']
        docs = []
        total_balance = 0
        total_invoice = 0
        total_residual = 0
        # BUG FIX: changed 'agent_id' to 'sales_man_id'
        domain=[('move_type','=','out_invoice'),('sales_man_id','!=',False)]

        domain+= dat['show_unpaid_only'] and [('amount_residual_signed', '>', 0)] or []
        domain+= len(dat['customer_ids']) > 0 and [('partner_id', 'in', dat['customer_ids'])] or []
        # BUG FIX: changed 'agent_id' to 'sales_man_id'
        domain+= len(dat['agent_ids']) > 0 and [('sales_man_id', 'in', dat['agent_ids'])] or []
        domain+=[('invoice_date','>=',dat['from_date'])]
        domain+=[('invoice_date','<=',dat['to_date'])]

        invoice_ids=self.env['account.move'].search(domain)
        # BUG FIX: changed 'agent_id.id' to 'sales_man_id.id'
        invoices_agents=invoice_ids.mapped('sales_man_id.id')
        invoice_ids_customer=invoice_ids.mapped('partner_id')

        for i in invoices_agents:
            all = []
            for c in invoice_ids_customer:
                invoices = []
                residual_amount = 0.0
                balance = 0.0

                # BUG FIX: changed 'inv.agent_id.id' to 'inv.sales_man_id.id'
                agent_invoices = invoice_ids.filtered(lambda inv: inv.sales_man_id.id==i and inv.partner_id==c)
                #raise UserError("%s"%agent_invoices)

                if agent_invoices:
                    invoices.append(agent_invoices)
                    residual_amount=sum(agent_invoices.mapped('amount_residual'))
                    balance=sum(agent_invoices.mapped('amount_total'))

                    total_balance += balance
                    total_invoice += residual_amount
                    cust = {
                        'customer': c.name,
                        'invoices': agent_invoices,
                        'invoice': residual_amount,
                        'balance': balance,
                    }
                    all.append(cust)
            if all:
                agent = self.env["res.partner"].browse(i)

                docs.append({
                    'agent': agent.name,
                    'data': all})

        return {
            'doc_ids': self.ids,
            'doc_model': 'agent.invoices.wiz',
            'docs': docs,
            'total_invoice': total_invoice,
            'total_balance': total_balance,
            'data': data['form'],
            'from': dat['from_date'],
            'to': dat['to_date']
        }
