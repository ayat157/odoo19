/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";

class StockBalanceReportWizard extends Component {
    static template = "dwave_stock_balance_report.DatePickerDialog";
     setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        this.state = useState({
            fromDate: firstDay.toISOString().split("T")[0],
            toDate: today.toISOString().split("T")[0],
            error: "",
            loading: false,
            based_on: "product",
            warehouse_type: "all",
            selectedWarehouses: [],
            warehouseSearch: "",
            showWarehouseDropdown: false,
            warehouses: [],
            selection_type: "all",
            selectedProducts: [],
            search: "",
            showDropdown: false,
            products: [],
            category_type: "all",
            selectedCategories: [],
            categorySearch: "",
            showCategoryDropdown: false,
            categories: [],
            ws_data: []
        });
        this.loadInitialData();
        this._onDocClick = (ev) => {
            if (!ev.target.closest(".skit-multi-select")) {
                this.state.showDropdown = false;
                this.state.showCategoryDropdown = false;
                this.state.showWarehouseDropdown = false;
            }
        };
        onMounted(() => document.addEventListener("click", this._onDocClick));
        onWillUnmount(() => document.removeEventListener("click", this._onDocClick));
    }

    _closeDialog() {
        this.env.services.action.doAction({
            type: "ir.actions.act_window_close",
        });
    }

    async loadInitialData() {
        try {
            this.state.products = await this.orm.searchRead(
                "product.product",
                [],
                ["display_name"]
            );

            this.state.categories = await this.orm.searchRead(
                "product.category",
                [],
                ["display_name"]
            );

            this.state.warehouses = await this.orm.searchRead(
                "stock.warehouse",
                [],
                ["display_name", "name"]
            );
        } catch (error) {
            console.error("Error loading initial data:", error);
            this.notification.add("Error loading data", { type: "danger" });
        }
    }

    // ============================================================
    // WAREHOUSE METHODS
    // ============================================================

    onChangeWarehouseType(ev) {
        this.state.warehouse_type = ev.target.value;
        this.state.error = "";
    }

    get filteredWarehouses() {
        const search = (this.state.warehouseSearch || "").toLowerCase();
        return this.state.warehouses.filter(w =>
            w.display_name.toLowerCase().includes(search)
        );
    }

    onWarehouseSearch(ev) {
        this.state.warehouseSearch = ev.target.value;
        this.state.showWarehouseDropdown = true;
    }

    showWarehouseDropdown() {
        this.state.showWarehouseDropdown = true;
    }

    toggleWarehouseDropdown() {
        this.state.showWarehouseDropdown = !this.state.showWarehouseDropdown;
    }

    addWarehouse(ev) {
        const id = parseInt(ev.currentTarget.dataset.id);
        const exists = this.state.selectedWarehouses.some(w => w.id === id);
        if (exists) return;

        const warehouse = this.state.warehouses.find(w => w.id === id);
        if (warehouse) {
            this.state.selectedWarehouses.push(warehouse);
        }
        this.state.warehouseSearch = "";
    }

    removeWarehouse(ev) {
        const id = parseInt(ev.currentTarget.dataset.id);
        this.state.selectedWarehouses = this.state.selectedWarehouses.filter(
            w => w.id !== id
        );
    }

    onChangeBasedOn(ev) {
        this.state.based_on = ev.target.value;
        this.state.error = "";
        if (this.state.based_on === "product") {
            this.state.category_type = "all";
            this.state.selectedCategories = [];
        }
        if (this.state.based_on === "category") {
            this.state.selection_type = "all";
            this.state.selectedProducts = [];
        }
    }

    onChangeSelectionType(ev) {
        this.state.selection_type = ev.target.value;
        this.state.error = "";
    }

    onChangeCategoryType(ev) {
        this.state.category_type = ev.target.value;
        this.state.error = "";
    }

    get filteredProducts() {
        const search = (this.state.search || "").toLowerCase();
        return this.state.products.filter(p =>
            p.display_name.toLowerCase().includes(search)
        );
    }

    onSearch(ev) {
        this.state.search = ev.target.value;
        this.state.showDropdown = true;
    }

    showDropdown() {
        this.state.showDropdown = true;
    }

    toggleDropdown() {
        this.state.showDropdown = !this.state.showDropdown;
    }

    addProduct(ev) {
        const id = parseInt(ev.currentTarget.dataset.id);
        const exists = this.state.selectedProducts.some(p => p.id === id);
        if (exists) return;

        const product = this.state.products.find(p => p.id === id);
        if (product) {
            this.state.selectedProducts.push(product);
        }
        this.state.search = "";
    }

    removeProduct(ev) {
        const id = parseInt(ev.currentTarget.dataset.id);
        this.state.selectedProducts = this.state.selectedProducts.filter(
            p => p.id !== id
        );
    }

    get filteredCategories() {
        const search = (this.state.categorySearch || "").toLowerCase();
        return this.state.categories.filter(c =>
            c.display_name.toLowerCase().includes(search)
        );
    }

    onCategorySearch(ev) {
        this.state.categorySearch = ev.target.value;
        this.state.showCategoryDropdown = true;
    }

    showCategoryDropdown() {
        this.state.showCategoryDropdown = true;
    }

    toggleCategoryDropdown() {
        this.state.showCategoryDropdown = !this.state.showCategoryDropdown;
    }

    addCategory(ev) {
        const id = parseInt(ev.currentTarget.dataset.id);
        const exists = this.state.selectedCategories.some(c => c.id === id);
        if (exists) return;
        const category = this.state.categories.find(c => c.id === id);
        if (category) {
            this.state.selectedCategories.push(category);
        }
        this.state.categorySearch = "";
    }

    removeCategory(ev) {
        const id = parseInt(ev.currentTarget.dataset.id);
        this.state.selectedCategories = this.state.selectedCategories.filter(
            c => c.id !== id
        );
    }

    validate() {
        if (!this.state.fromDate || !this.state.toDate) {
            this.state.error = "Please select both dates";
            return false;
        }
        if (new Date(this.state.fromDate) > new Date(this.state.toDate)) {
            this.state.error = "From Date cannot be later than To Date";
            return false;
        }
        if (
            this.state.warehouse_type === "warehouse" &&
            !this.state.selectedWarehouses.length
        ) {
            this.state.error = "Please select at least one warehouse";
            return false;
        }
        if (
            this.state.based_on === "product" &&
            this.state.selection_type === "product" &&
            !this.state.selectedProducts.length
        ) {
            this.state.error = "Please select at least one product";
            return false;
        }
        if (
            this.state.based_on === "category" &&
            this.state.category_type === "category" &&
            !this.state.selectedCategories.length
        ) {
            this.state.error = "Please select at least one category";
            return false;
        }
        this.state.error = "";
        return true;
    }

    // ============================================================
    // EXPORT METHODS
    // ============================================================

    async onGenerateSummary() {
        if (!this.validate()) return;
        this.state.loading = true;

        try {
            await this.loadXLSX();
            await this.generateSummaryReport();
            this.notification.add("Summary generated successfully!", { type: "success" });
        } catch (error) {
            console.error(error);
            this.notification.add("Error generating summary: " + error.message, { type: "danger" });
        }
        this.state.loading = false;
    }

    async onGenerate() {
        if (!this.validate()) return;
        this.state.loading = true;

        try {
            await this.loadXLSX();
            await this.generateExcelReport();
            this.notification.add("Excel exported successfully!", { type: "success" });
            this._closeDialog();
        } catch (error) {
            console.error("Excel Generation Error:", error);
            this.notification.add("Error generating Excel: " + error.message, { type: "danger" });
        }

        this.state.loading = false;
    }

    async onPrintPDF() {
        if (!this.validate()) return;
        this.state.loading = true;

        try {
            await this.loadPDF();
            await this.generatePDFReport();
            this.notification.add("PDF exported successfully!", { type: "success" });
            this._closeDialog();
        } catch (error) {
            console.error("PDF Generation Error:", error);
            this.notification.add("Error generating PDF: " + error.message, { type: "danger" });
        }

        this.state.loading = false;
    }

    async loadXLSX() {
        if (window.XLSX) return;
        
        return new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.min.js";
            script.async = true;
            script.onload = () => {
                console.log("XLSX loaded successfully");
                resolve();
            };
            script.onerror = () => {
                console.error("Failed to load XLSX");
                reject(new Error("Failed to load XLSX library"));
            };
            document.head.appendChild(script);
        });
    }

    async loadPDF() {
        if (window.jsPDF && window.html2pdf) return;

        return new Promise((resolve, reject) => {
            const script1 = document.createElement("script");
            script1.src = "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js";
            script1.async = true;
            script1.onload = () => {
                const script2 = document.createElement("script");
                script2.src = "https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.28/jspdf.plugin.autotable.min.js";
                script2.async = true;
                script2.onload = () => {
                    console.log("PDF libraries loaded successfully");
                    resolve();
                };
                script2.onerror = () => reject(new Error("Failed to load PDF AutoTable"));
                document.head.appendChild(script2);
            };
            script1.onerror = () => reject(new Error("Failed to load jsPDF"));
            document.head.appendChild(script1);
        });
    }

    async generateExcelReport() {
        try {
            if (!window.XLSX) {
                throw new Error("XLSX library not loaded");
            }

            const stockMoves = await this.fetchStockMovesData();
            
            if (!stockMoves || stockMoves.length === 0) {
                this.notification.add("No data found for the selected filters", { type: "warning" });
                return;
            }

            const workbook = XLSX.utils.book_new();

            // ورقة التفاصيل
            const detailsData = stockMoves.map(move => ({
                "Date": move.date?.split(" ")[0] || "",
                "Reference": move.reference || "",
                "Product": move.product_id?.[1] || "",
                "Warehouse": move.warehouse_id?.[1] || "",
                "From Location": move.location_id?.[1] || "",
                "To Location": move.location_dest_id?.[1] || "",
                "Quantity": move.qty_done || 0
            }));

            const detailsSheet = XLSX.utils.json_to_sheet(detailsData);
            detailsSheet['!cols'] = [
                { wch: 12 },
                { wch: 15 },
                { wch: 20 },
                { wch: 15 },
                { wch: 18 },
                { wch: 18 },
                { wch: 10 }
            ];
            XLSX.utils.book_append_sheet(workbook, detailsSheet, "Stock Movements");

            // ورقة الملخص
            const summaryData = this.generateSummaryData(stockMoves);
            const summarySheet = XLSX.utils.json_to_sheet(summaryData);
            summarySheet['!cols'] = [
                { wch: 20 },
                { wch: 12 },
                { wch: 12 },
                { wch: 12 },
                { wch: 15 }
            ];
            XLSX.utils.book_append_sheet(workbook, summarySheet, "Summary");

            // حفظ الملف
            const fileName = `Stock_Report_${new Date().toISOString().split('T')[0]}.xlsx`;
            XLSX.writeFile(workbook, fileName);
            
        } catch (error) {
            console.error("Excel generation error:", error);
            throw error;
        }
    }

    async generateSummaryReport() {
        try {
            if (!window.XLSX) {
                throw new Error("XLSX library not loaded");
            }

            const stockMoves = await this.fetchStockMovesData();
            
            if (!stockMoves || stockMoves.length === 0) {
                this.notification.add("No data found for the selected filters", { type: "warning" });
                return;
            }

            const workbook = XLSX.utils.book_new();
            const summaryData = this.generateSummaryData(stockMoves);
            
            const ws = XLSX.utils.json_to_sheet(summaryData);
            ws['!cols'] = [
                { wch: 20 },
                { wch: 12 },
                { wch: 12 },
                { wch: 12 },
                { wch: 15 }
            ];
            
            XLSX.utils.book_append_sheet(workbook, ws, "Summary");
            
            const fileName = `Summary_Report_${new Date().toISOString().split('T')[0]}.xlsx`;
            XLSX.writeFile(workbook, fileName);
            
        } catch (error) {
            console.error("Summary generation error:", error);
            throw error;
        }
    }

    generateSummaryData(stockMoves) {
        const summary = {};

        // معالجة كل حركة
        stockMoves.forEach(move => {
            const warehouseId = move.warehouse_id?.[0] || "Unknown";
            const warehouseName = move.warehouse_id?.[1] || "Unknown Warehouse";
            
            if (!summary[warehouseId]) {
                summary[warehouseId] = {
                    "Warehouse": warehouseName,
                    "Inbound": 0,
                    "Outbound": 0,
                    "Damage": 0
                };
            }

            const src = move.location_id?.[1] || "";
            const dest = move.location_dest_id?.[1] || "";
            const qty = move.qty_done || 0;

            // تصنيف الحركات بناءً على الموقع
            if ((src.includes("Vendor") || src.includes("supplier") || src.includes("Supplier")) && 
                dest.includes("Stock")) {
                summary[warehouseId]["Inbound"] += qty;
            } else if (src.includes("Stock") && 
                      (dest.includes("Customer") || dest.includes("customer"))) {
                summary[warehouseId]["Outbound"] += qty;
            } else if (src.includes("Stock") && 
                      (dest.includes("Damage") || dest.includes("damage"))) {
                summary[warehouseId]["Damage"] += qty;
            }
        });

        // تحويل إلى مصفوفة وإضافة الإجمالي
        const result = Object.values(summary).map(item => ({
            "Warehouse": item["Warehouse"],
            "Inbound": item["Inbound"],
            "Outbound": item["Outbound"],
            "Damage": item["Damage"],
            "Net Change": item["Inbound"] - item["Outbound"] - item["Damage"]
        }));

        // إضافة صف الإجمالي
        const totals = result.reduce((acc, row) => ({
            "Warehouse": "TOTAL",
            "Inbound": acc["Inbound"] + row["Inbound"],
            "Outbound": acc["Outbound"] + row["Outbound"],
            "Damage": acc["Damage"] + row["Damage"],
            "Net Change": 0
        }), {
            "Warehouse": "",
            "Inbound": 0,
            "Outbound": 0,
            "Damage": 0,
            "Net Change": 0
        });

        totals["Net Change"] = totals["Inbound"] - totals["Outbound"] - totals["Damage"];
        result.push(totals);

        return result;
    }

    async generatePDFReport() {
        try {
            if (!window.jsPDF) {
                throw new Error("jsPDF library not loaded");
            }

            const { jsPDF } = window.jspdf;
            const stockMoves = await this.fetchStockMovesData();
            
            if (!stockMoves || stockMoves.length === 0) {
                this.notification.add("No data found for the selected filters", { type: "warning" });
                return;
            }

            const doc = new jsPDF({
                orientation: "landscape",
                unit: "pt",
                format: "a4",
            });

            const pageWidth = doc.internal.pageSize.getWidth();

            // العنوان
            doc.setFont("helvetica", "bold");
            doc.setFontSize(16);
            doc.text("STOCK BALANCE REPORT", pageWidth / 2, 40, { align: "center" });

            // رأس التقرير
            doc.setFont("helvetica", "normal");
            doc.setFontSize(10);
            doc.text(
                `From: ${this.state.fromDate}  to  ${this.state.toDate}`,
                pageWidth / 2,
                58,
                { align: "center" }
            );

            // تحضير بيانات الجدول
            const tableData = stockMoves.map(move => [
                move.date?.split(" ")[0] || "",
                move.reference || "-",
                move.product_id?.[1] || "",
                move.warehouse_id?.[1] || "",
                move.location_id?.[1] || "",
                move.location_dest_id?.[1] || "",
                (move.qty_done || 0).toString()
            ]);

            doc.autoTable({
                head: [[
                    "Date", "Reference", "Product", "Warehouse",
                    "From Location", "To Location", "Quantity"
                ]],
                body: tableData,
                startY: 90,
                theme: "grid",
                showHead: "firstPage",
                styles: {
                    font: "helvetica",
                    fontSize: 8,
                    cellPadding: 3,
                },
                headStyles: {
                    fillColor: [79, 129, 189],
                    textColor: [255, 255, 255],
                    fontStyle: "bold",
                    halign: "center",
                },
                columnStyles: {
                    0: { cellWidth: 55, halign: "center" },
                    6: { cellWidth: 50, halign: "right" },
                },
                alternateRowStyles: {
                    fillColor: [248, 249, 250]
                },
                margin: { top: 40, left: 10, right: 10, bottom: 40 },
            });

            doc.save(`Stock_Report_${new Date().toISOString().split('T')[0]}.pdf`);
            
        } catch (error) {
            console.error("PDF generation error:", error);
            throw error;
        }
    }

    async fetchStockMovesData() {
        try {
            let domain = [
                ['date', '>=', this.state.fromDate + ' 00:00:00'],
                ['date', '<=', this.state.toDate + ' 23:59:59'],
                ['state', '=', 'done'],
            ];

            if (this.state.warehouse_type === 'warehouse' && this.state.selectedWarehouses.length > 0) {
                const warehouseIds = this.state.selectedWarehouses.map(w => w.id);
                domain.push(['location_id.warehouse_id', 'in', warehouseIds]);
            }

            const stockMoves = await this.orm.searchRead(
                'stock.move.line',
                domain,
                ['date', 'reference', 'picking_id', 'location_id', 'location_dest_id', 
                 'qty_done', 'product_id', 'warehouse_id']
            );

            return stockMoves;
        } catch (error) {
            console.error("Error fetching stock moves data:", error);
            throw error;
        }
    }
}

registry.category("actions").add(
    "dwave_stock_balance_report.open_wizard",
    StockBalanceReportWizard
);
