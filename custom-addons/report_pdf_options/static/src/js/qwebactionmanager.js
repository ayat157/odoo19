/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { PdfOptionsModal } from "./PdfOptionsModal";
import { rpc } from "@web/core/network/rpc";
import { getReportUrl, downloadReport } from "@web/webclient/actions/reports/utils";

function getWKHTMLTOPDF_MESSAGES(status) {
    const link = '<br><br><a href="http://wkhtmltopdf.org/" target="_blank">wkhtmltopdf.org</a>'; // FIXME missing markup
    const _status = {
        broken:
            _t(
                "Your installation of Wkhtmltopdf seems to be broken. The report will be shown in html."
            ) + link,
        install:
            _t("Unable to find Wkhtmltopdf on this system. The report will be shown in html.") +
            link,
        upgrade:
            _t(
                "You should upgrade your version of Wkhtmltopdf to at least 0.12.0 in order to get a correct display of headers and footers as well as support for table-breaking between pages."
            ) + link,
        workers: _t(
            "You need to start Odoo with at least two workers to print a pdf version of the reports."
        ),
    };
    return _status[status];
}

let iframeForReport;

function printPdf(url, callback) {
    let iframe = iframeForReport;
    if (!iframe) {
        iframe = iframeForReport = document.createElement('iframe');
        iframe.className = 'pdfIframe'
        document.body.appendChild(iframe);
        iframe.style.display = 'none';
        iframe.onload = function () {
            setTimeout(function () {
                iframe.focus();
                iframe.contentWindow.print();
                URL.revokeObjectURL(url)
                callback();
            }, 1);
        };
    }
    iframe.src = url;
}

let wkhtmltopdfStateProm;

registry
    .category("ir.actions.report handlers")
    .add("pdf_report_options_handler", async function (action, options, env) {
        let { default_print_option, report_type } = action;
        if (report_type !== "qweb-pdf")
            return false;
        if (default_print_option === "download") {
            const downloadContext = { ...env.services.user.context };
            if (action.context) {
                Object.assign(downloadContext, action.context);
            }
            const { success, message } = await downloadReport(rpc, action, "pdf", downloadContext);
            if (message) {
                env.services.notification.add(message, {
                    sticky: true,
                    title: _t("Report"),
                });
            }
            return success;
        }
        if (!default_print_option) {
            let removeDialog;
            default_print_option = await new Promise(resolve => {
                removeDialog = env.services.dialog.add(
                    PdfOptionsModal,
                    {
                        onSelectOption: (option) => {
                            return resolve(option);
                        }
                    },
                    {
                        onClose: () => {
                            resolve("close");
                        }
                    }
                );
            });
            removeDialog();
            if (default_print_option === "close") {
                return true;
            }
        }

        // if the user wants a download, let the standard report action perform it
        if (default_print_option === "download") {
            return false;
        }

        // check the state of wkhtmltopdf before proceeding
        if (!wkhtmltopdfStateProm) {
            wkhtmltopdfStateProm = await rpc("/report/check_wkhtmltopdf");
        }
        const state = wkhtmltopdfStateProm;
        // display a notification according to wkhtmltopdf's state
        const message = getWKHTMLTOPDF_MESSAGES(state)
        if (message) {
            env.services.notification.add(message, {
                sticky: true,
                title: _t("Report"),
            });
        }
        if (["upgrade", "ok"].includes(state)) {
            const url = getReportUrl(action, "pdf");
            if (default_print_option === "print") {
                env.services.ui.block();
                printPdf(url, () => {
                    env.services.ui.unblock();
                });
                return true;
            }
            if (default_print_option === "open") {
                window.open(url);
                return true;
            }
            // download should never reach this point because it returns false above
            return false;
        } else {
            // let the default report action show the report in html if PDF generation fails
            return false;
        }
    })
