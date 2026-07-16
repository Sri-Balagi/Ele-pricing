import hashlib
import time
from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.constants import ExportFormat
from app.export.base_exporter import BaseExporter
from app.models.domain import ExportContext, ExportReport


class PDFExporter(BaseExporter):
    """
    Exports the Configuration to a professional PDF Quote using reportlab.
    Includes PDF document metadata and required sections.
    """

    def export(self, context: ExportContext) -> ExportReport:
        t0 = time.perf_counter()
        config = context.configuration
        quote = config.quote_metadata
        price = config.pricing_summary

        buffer = BytesIO()

        # Meta properties for the PDF file itself
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            title=f"Quote {quote.quote_number if quote else 'DRAFT'}",
            author="Elevator Configuration Engine",
            subject=f"Configuration {config.configuration_id}",
        )

        # We can add custom metadata properties in ReportLab canvas during build if needed,
        # but title/author/subject covers standard PDF metadata.

        styles = getSampleStyleSheet()
        elements = []

        # 1. Company Header
        header_style = ParagraphStyle("Header", parent=styles["Heading1"], alignment=1)
        elements.append(
            Paragraph("Elevator Configuration & Pricing Engine", header_style)
        )
        elements.append(Spacer(1, 12))

        # 2. Metadata Section (Customer Reference, Quote Number, Date, Validity, Config ID, Correlation ID)
        elements.append(Paragraph("<b>Quote Information</b>", styles["Heading2"]))

        quote_num = quote.quote_number if quote else "DRAFT"
        q_date = context.execution_timestamp
        q_valid = quote.valid_until if quote else "N/A"

        meta_data = [
            ["Quote Number:", quote_num],
            ["Customer Reference:", config.customer_reference or "N/A"],
            ["Generated Date:", q_date],
            ["Valid Until:", q_valid],
            ["Configuration ID:", config.configuration_id],
            ["Correlation ID:", context.correlation_id],
            ["Generator Version:", "1.0"],
        ]

        meta_table = Table(meta_data, hAlign="LEFT")
        meta_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(meta_table)
        elements.append(Spacer(1, 12))

        # 3. Selected Features
        elements.append(
            Paragraph("<b>Configuration Summary (Features)</b>", styles["Heading2"])
        )
        if not config.selected_feature_options:
            elements.append(Paragraph("None", styles["Normal"]))
        else:
            if context.catalogue:
                for opt_id in config.selected_feature_options:
                    opt = next(
                        (
                            o
                            for o in context.catalogue.feature_options
                            if o.id == opt_id
                        ),
                        None,
                    )
                    if opt:
                        feat = next(
                            (
                                f
                                for f in context.catalogue.features
                                if f.id == opt.feature_id
                            ),
                            None,
                        )
                        if feat:
                            text = f"• {feat.name}: {opt.display_name}"
                        else:
                            text = f"• {opt.display_name}"
                    else:
                        text = f"• {opt_id}"
                    elements.append(Paragraph(text, styles["Normal"]))
            else:
                for opt_id in config.selected_feature_options:
                    elements.append(Paragraph(f"• {opt_id}", styles["Normal"]))

        elements.append(Spacer(1, 12))

        # 4. Bill Of Materials
        elements.append(Paragraph("<b>Bill of Materials</b>", styles["Heading2"]))
        currency = price.currency_symbol if price else "$"

        if config.bill_of_materials and config.bill_of_materials.items:
            base_items = [
                i
                for i in config.bill_of_materials.items
                if getattr(i.origin_type, "value", str(i.origin_type)) == "BASE"
            ]
            feature_items = [
                i
                for i in config.bill_of_materials.items
                if getattr(i.origin_type, "value", str(i.origin_type)) != "BASE"
            ]

            def create_bom_table(items_list, title):
                elements.append(Paragraph(f"<b>{title}</b>", styles["Heading3"]))
                table_data = [["Component ID", "Component Name", "Qty", "Unit Cost"]]
                total = Decimal("0.00")
                for item in items_list:
                    comp_name = item.component_id
                    if context.catalogue:
                        comp = next(
                            (
                                c
                                for c in context.catalogue.components
                                if c.id == item.component_id
                            ),
                            None,
                        )
                        if comp:
                            comp_name = comp.name
                    cost_val = (
                        item.unit_cost
                        if item.unit_cost is not None
                        else Decimal("0.00")
                    )
                    total += cost_val
                    table_data.append(
                        [
                            item.component_id,
                            comp_name,
                            str(item.quantity),
                            f"{currency}{cost_val:.2f}",
                        ]
                    )

                table_data.append(["", "", "Total:", f"{currency}{total:.2f}"])

                t = Table(table_data, hAlign="LEFT")
                t.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("FONTNAME", (-2, -1), (-1, -1), "Helvetica-Bold"),
                        ]
                    )
                )
                elements.append(t)
                elements.append(Spacer(1, 12))

            if base_items:
                create_bom_table(base_items, "Base Build Components")
            if feature_items:
                create_bom_table(feature_items, "Feature Customization Components")
        else:
            elements.append(Paragraph("No components generated.", styles["Normal"]))
            elements.append(Spacer(1, 12))

        # 5. Pricing Breakdown
        elements.append(Paragraph("<b>Pricing Breakdown</b>", styles["Heading2"]))
        price_data = [["Description", "Amount"]]
        if price:
            price_data.append(["Base Cost", f"{currency}{price.category_cost:.2f}"])
            price_data.append(["Feature Cost", f"{currency}{price.feature_cost:.2f}"])
            if price.floor_coverage_cost > 0:
                price_data.append(
                    [
                        "Additional Floor Coverage",
                        f"{currency}{price.floor_coverage_cost:.2f}",
                    ]
                )
            price_data.append(
                ["Subtotal before tax", f"{currency}{price.subtotal_before_tax:.2f}"]
            )
            price_data.append(["Tax amount", f"{currency}{price.tax_amount:.2f}"])
            price_data.append(["Grand total", f"{currency}{price.total_after_tax:.2f}"])

        price_table = Table(price_data, hAlign="LEFT")
        price_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    (
                        "FONTNAME",
                        (0, -1),
                        (-1, -1),
                        "Helvetica-Bold",
                    ),  # Bold Grand total
                ]
            )
        )
        elements.append(price_table)
        elements.append(Spacer(1, 12))

        # Add Logistics Exclusion Line
        elements.append(
            Paragraph(
                "<i>This cost is exclusive of Logistics Cost</i>", styles["Normal"]
            )
        )
        elements.append(Spacer(1, 24))

        # 6. Footer
        elements.append(
            Paragraph(
                "<i>Generated by Elevator Configuration Engine</i>", styles["Normal"]
            )
        )

        doc.build(elements)
        content_bytes = buffer.getvalue()
        buffer.close()

        checksum = hashlib.sha256(content_bytes).hexdigest()
        file_size = len(content_bytes)
        generation_time_ms = (time.perf_counter() - t0) * 1000

        return ExportReport(
            export_format=ExportFormat.PDF,
            filename=f"{config.configuration_id}.pdf",
            mime_type="application/pdf",
            checksum=checksum,
            file_size=file_size,
            generation_time_ms=generation_time_ms,
            success=True,
            content=content_bytes,
        )
