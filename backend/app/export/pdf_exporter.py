import time
import hashlib
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
            subject=f"Configuration {config.configuration_id}"
        )
        
        # We can add custom metadata properties in ReportLab canvas during build if needed,
        # but title/author/subject covers standard PDF metadata.
        
        styles = getSampleStyleSheet()
        elements = []
        
        # 1. Company Header
        header_style = ParagraphStyle('Header', parent=styles['Heading1'], alignment=1)
        elements.append(Paragraph("Elevator Configuration & Pricing Engine", header_style))
        elements.append(Spacer(1, 12))
        
        # 2. Metadata Section (Customer Reference, Quote Number, Date, Validity, Config ID, Correlation ID)
        elements.append(Paragraph("<b>Quote Information</b>", styles['Heading2']))
        
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
            ["Generator Version:", "1.0"]
        ]
        
        meta_table = Table(meta_data, hAlign='LEFT')
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))
        
        # 3. Selected Features
        elements.append(Paragraph("<b>Configuration Summary (Features)</b>", styles['Heading2']))
        features_str = ", ".join(config.selected_feature_options)
        elements.append(Paragraph(features_str or "None", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # 4. Bill Of Materials
        elements.append(Paragraph("<b>Bill of Materials</b>", styles['Heading2']))
        bom_data = [["Component ID", "Quantity", "Origin", "Reason"]]
        if config.bill_of_materials:
            for item in config.bill_of_materials.items:
                bom_data.append([
                    item.component_id, 
                    str(item.quantity), 
                    item.origin_type.value, 
                    item.reason
                ])
        else:
            bom_data.append(["No components", "", "", ""])
            
        bom_table = Table(bom_data, hAlign='LEFT')
        bom_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(bom_table)
        elements.append(Spacer(1, 12))
        
        # 5. Pricing Breakdown
        elements.append(Paragraph("<b>Pricing Breakdown</b>", styles['Heading2']))
        price_data = [["Description", "Amount"]]
        if price:
            currency = price.currency_symbol
            price_data.append(["Component Costs", f"{currency}{price.component_cost}"])
            price_data.append(["Feature Costs", f"{currency}{price.feature_cost}"])
            price_data.append(["Subtotal Before Tax", f"{currency}{price.subtotal_before_tax}"])
            price_data.append(["Tax Amount", f"{currency}{price.tax_amount}"])
            price_data.append(["Grand Total", f"{currency}{price.total_after_tax}"])
            
        price_table = Table(price_data, hAlign='LEFT')
        price_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'), # Bold Grand total
        ]))
        elements.append(price_table)
        elements.append(Spacer(1, 24))
        
        # 6. Footer
        elements.append(Paragraph("<i>Generated by Elevator Configuration Engine</i>", styles['Normal']))
        
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
            content=content_bytes
        )
