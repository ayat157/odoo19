# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError
import io
import base64


class PurchaseVatReportWizard(models.TransientModel):
    _name = "dwave.purchase.vat.report.wizard"
    _description = "Purchase VAT Recovery Report Wizard"

    date_from = fields.Date(
        string="From Date",
        required=True,
        default=fields.Date.context_today,
    )

    date_to = fields.Date(
        string="To Date",
        required=True,
        default=fields.Date.context_today,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    partner_ids = fields.Many2many(
        "res.partner",
        string="Vendors",
        domain=[("supplier_rank", ">", 0)],
    )

    tax_id = fields.Many2one(
        "account.tax",
        string="Purchase Tax",
        domain=[
            ("type_tax_use", "=", "purchase")
        ],
    )

    xlsx_file = fields.Binary(
        string="Excel File",
        readonly=True,
    )

    xlsx_filename = fields.Char(
        string="Filename",
        readonly=True,
    )


    def _get_purchase_moves(self):
        """
        Get posted vendor bills
        """

        domain = [
            ("move_type", "=", "in_invoice"),
            ("state", "=", "posted"),
            ("company_id", "=", self.company_id.id),
            ("invoice_date", ">=", self.date_from),
            ("invoice_date", "<=", self.date_to),
        ]

        if self.partner_ids:
            domain.append(
                ("partner_id", "in", self.partner_ids.ids)
            )

        moves = self.env["account.move"].search(
            domain,
            order="invoice_date asc"
        )

        if not moves:
            raise UserError(
                _("No posted vendor bills found.")
            )

        return moves


    def _prepare_report_data(self):

        moves = self._get_purchase_moves()

        lines = []

        for move in moves:

            tax_amount = 0.0
            tax_rate = 0.0

            for line in move.invoice_line_ids:

                taxes = line.tax_ids

                if self.tax_id:
                    taxes = taxes.filtered(
                        lambda t: t.id == self.tax_id.id
                    )

                for tax in taxes:
                    tax_rate = tax.amount

                    tax_amount += (
                        line.price_subtotal
                        * tax.amount
                        / 100
                    )


            if self.tax_id and not tax_amount:
                continue


            lines.append({

                "date": move.invoice_date,

                "vendor": move.partner_id.name,

                "bill_number": move.name,

                "untaxed": move.amount_untaxed,

                "tax_rate": tax_rate,

                "tax_amount": tax_amount,

                "total": (
                    move.amount_untaxed
                    + tax_amount
                ),

            })


        if not lines:
            raise UserError(
                _("No invoices match selected tax.")
            )

        return {

            "company": self.company_id.name,

            "date_from": self.date_from,

            "date_to": self.date_to,

            "tax": (
                self.tax_id.name
                if self.tax_id
                else "All Taxes"
            ),

            "lines": lines,

        }


    def action_print_pdf(self):

        data = self._prepare_report_data()

        return self.env.ref(
            "dwave_purchase_vat_report.action_purchase_vat_report"
        ).report_action(
            self,
            data=data
        )


    def action_export_xlsx(self):

        import xlsxwriter

        data = self._prepare_report_data()

        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(
            output,
            {
                "in_memory": True
            }
        )

        sheet = workbook.add_worksheet(
            "Purchase VAT"
        )


        headers = [
            "Date",
            "Vendor",
            "Bill Number",
            "Untaxed Amount",
            "VAT %",
            "VAT Amount",
            "Total",
        ]


        bold = workbook.add_format(
            {
                "bold": True
            }
        )


        for col, header in enumerate(headers):
            sheet.write(
                0,
                col,
                header,
                bold
            )


        row = 1

        for line in data["lines"]:

            sheet.write(
                row,
                0,
                str(line["date"])
            )

            sheet.write(
                row,
                1,
                line["vendor"]
            )

            sheet.write(
                row,
                2,
                line["bill_number"]
            )

            sheet.write(
                row,
                3,
                line["untaxed"]
            )

            sheet.write(
                row,
                4,
                line["tax_rate"]
            )

            sheet.write(
                row,
                5,
                line["tax_amount"]
            )

            sheet.write(
                row,
                6,
                line["total"]
            )

            row += 1


        workbook.close()

        output.seek(0)

        file = base64.b64encode(
            output.read()
        )


        self.write({

            "xlsx_file": file,

            "xlsx_filename":
                "purchase_vat_report.xlsx"

        })


        return {

            "type": "ir.actions.act_url",

            "url":
                "/web/content/?model=dwave.purchase.vat.report.wizard"
                "&id=%s"
                "&field=xlsx_file"
                "&filename_field=xlsx_filename"
                "&download=true"
                % self.id,

            "target": "self",

        }
