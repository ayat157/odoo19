# -*- coding: utf-8 -*-
from odoo import models, api
from . import salesman_statement_base # Import the shared logic

# Inherit from Odoo's AbstractModel and our Base class
class SalesmanStatementReportAR(models.AbstractModel, salesman_statement_base.SalesmanStatementBase):
    # --- THIS IS THE FIX ---
    # Shortened the name to be under the 63-character limit
    _name = 'report.dwave_agent_salesman.statement_template_ar'
    _description = 'Salesman Customer Statement Report (AR)'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Call the shared logic from the base class
        return self._get_report_data(docids, data)

    def _get_report_data(self, docids, data):
        wizard = self.env['salesman.statement.wiz'].browse(docids)

        # ensure data exists
        data = data or {}

        return {
            'doc_ids': wizard.ids,
            'doc_model': 'salesman.statement.wiz',
            'docs': wizard,
            'doc': wizard,

            # 🔥 FIX: Provide all QWeb template variables
            'salesman': wizard.salesman_id,
            'company': wizard.company_id or self.env.company,
            'res_company': wizard.company_id or self.env.company,
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'user': self.env.user,

            # table data
            'lines': data.get('lines', []),
            'totals': data.get('totals', {}),
        }


