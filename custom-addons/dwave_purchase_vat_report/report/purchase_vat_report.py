# -*- coding: utf-8 -*-

from odoo import models


class PurchaseVatReport(models.AbstractModel):
    _name = "report.dwave_purchase_vat_report.purchase_vat_report"
    _description = "Purchase VAT Recovery Report"


    def _get_report_values(self, docids, data=None):

        data = data or {}

        lines = data.get("lines", [])

        total_untaxed = 0.0
        total_tax = 0.0
        total_amount = 0.0


        for line in lines:

            total_untaxed += line.get(
                "untaxed",
                0.0
            )

            total_tax += line.get(
                "tax_amount",
                0.0
            )

            total_amount += line.get(
                "total",
                0.0
            )


        docs = self.env[
            "dwave.purchase.vat.report.wizard"
        ].browse(docids)


        return {

            "doc_ids": docids,

            "doc_model":
                "dwave.purchase.vat.report.wizard",

            "docs": docs,


            "company":
                data.get(
                    "company",
                    ""
                ),


            "date_from":
                data.get(
                    "date_from"
                ),


            "date_to":
                data.get(
                    "date_to"
                ),


            "tax":
                data.get(
                    "tax",
                    "All Taxes"
                ),


            "lines":
                lines,


            "total_untaxed":
                total_untaxed,


            "total_tax":
                total_tax,


            "total_amount":
                total_amount,

        }
