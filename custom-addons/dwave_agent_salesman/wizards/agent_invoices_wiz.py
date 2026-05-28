from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AgentInvoicesWiz(models.TransientModel):
    _name = "agent.invoices.wiz"
    _description = "Agent Invoices Print"

    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)

    agent_ids = fields.Many2many(comodel_name="res.partner",
                                 relation="agent_wiz_rel",
                                 column1="agent_id",
                                 column2="wiz_id",
                                 string="Agents", domain=[('agent', '=', True)])
    customer_ids = fields.Many2many(comodel_name="res.partner",
                                    relation="customer_wiz_rel",
                                    column1="customer_id",
                                    column2="wiz_id", string="Customers")
    show_unpaid_only = fields.Boolean(string="Show Unpaid Invoices Only", default=True)

    @api.onchange("agent_ids")
    def get_agents_customers(self):
        # BUG FIX: changed 'agent_id' to 'sales_man_id' to match models/sale_order.py
        customers = self.env['sale.order'].search([('sales_man_id', 'in', self.agent_ids.ids)]).mapped('partner_id')
        return {'domain': {'customer_ids': [('id', 'in', customers.ids)]}}

    def print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': self.from_date,
                'to_date': self.to_date,
                'agent_ids': self.agent_ids.ids,
                'customer_ids': self.customer_ids.ids,
                'show_unpaid_only': self.show_unpaid_only,
            },
        }

        # Build dynamic file name
        filename = f"Agent_invoice_{self.from_date or ''}_to_{self.to_date or ''}.pdf"

        # ✅ Use the report action reference — this is key
        action = self.env.ref('dwave_agent_salesman.agent_invoices_id').report_action(
            self,
            data=data
        )

        # ✅ Set the file name on the action (this one is respected)
        action['name'] = filename
        return action
