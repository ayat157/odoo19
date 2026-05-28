# -*- coding: utf-8 -*-
from odoo import models, api
from . import salesman_statement_base # Import the shared logic

# Inherit from Odoo's AbstractModel and our Base class
class SalesmanStatementReportEN(models.AbstractModel, salesman_statement_base.SalesmanStatementBase):
    # --- THIS IS THE FIX ---
    # Shortened the name to be under the 63-character limit
    _name = 'report.dwave_agent_salesman.statement_template_en'
    _description = 'Salesman Customer Statement Report (EN)'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Call the shared logic from the base class
        return self._get_report_data(docids, data)