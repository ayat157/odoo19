# -*- coding: utf-8 -*-
{
    "name": "Dwave Stock Balance Report",
    'version': '19.0.1.0.0',
    'category': 'Inventory/Reporting',
    'summary': 'Generate Stock Balance reports for any product, category or date range — export as PDF or Excel in one click.',
    'description': """
        Stock Balance Report lets you generate detailed stock movement reports
        for all or specific products and categories over any date range,
        grouped by Product or by Category and Product. Export every report as
        a print-ready PDF or styled Excel file in just one click.
    """,
    'author': 'Srikesh Infotech',
    'license': "OPL-1",
    'website': 'http://www.srikeshinfotech.com',
    'images': ['images/banner.gif'],
    "depends": ["stock", "web"],
    "data": [
        "views/action.xml",
        "views/stock_menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "dwave_stock_balance_report/static/src/css/stock_report_popup.css",
            "dwave_stock_balance_report/static/src/js/stock_report_balance.js",
            "dwave_stock_balance_report/static/src/xml/stock_report_popup.xml",
            "https://cdn.jsdelivr.net/npm/xlsx-js-style@1.2.0/dist/xlsx.bundle.js",
        ],
    },
    "installable": True,
    'application': True,
}
