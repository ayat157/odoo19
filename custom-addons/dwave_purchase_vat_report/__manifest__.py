# -*- coding: utf-8 -*-

{
    "name": "DWave Purchase VAT Report",
    "version": "19.0.1.0.0",
    "category": "Accounting/Reporting",
    "summary": "Purchase VAT Recovery Report",
    "description": """
        Purchase VAT Recovery Report
        ============================

        Features:
        - Purchase VAT report
        - Filter by date
        - Filter by vendor
        - Filter by tax
        - PDF report
        - Excel export
    """,

    "author": "DWave",
    "license": "LGPL-3",

    "depends": [
        "account",
    ],

    "data": [
         "views/purchase_vat_views.xml",
         "report/purchase_vat_report.xml",
        "report/purchase_vat_template.xml",

   ],

    "installable": True,
    "application": True,
    "auto_install": False,
}
