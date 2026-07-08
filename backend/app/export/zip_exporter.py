import io
import json
import zipfile
import hashlib
from datetime import datetime, timezone

from app.export.base_exporter import BaseExporter
from app.models.domain import ExportContext, ExportReport, ExportManifest
from app.core.constants import ExportFormat
from app.export.json_exporter import JSONExporter
from app.export.pdf_exporter import PDFExporter
from app.export.excel_exporter import ExcelExporter

class ZIPExporter(BaseExporter):
    """
    Generates a complete ZIP bundle containing the Configuration (JSON), 
    Quote (PDF), BOM (Excel), and an ExportManifest.
    """
    
    def export(self, context: ExportContext) -> ExportReport:
        # 1. Generate individual formats
        json_report = JSONExporter().export(context)
        pdf_report = PDFExporter().export(context)
        excel_report = ExcelExporter().export(context)
        
        if not json_report.success or not pdf_report.success or not excel_report.success:
            return ExportReport(
                export_format=ExportFormat.ZIP,
                filename="error.zip",
                mime_type="application/zip",
                checksum="",
                file_size=0,
                success=False,
                warnings=["Failed to generate one or more artifacts for the ZIP bundle."]
            )
            
        # 2. Build manifest
        manifest = ExportManifest(
            configuration_id=context.configuration.configuration_id,
            quote_number=context.configuration.quote_metadata.quote_number if context.configuration.quote_metadata else None,
            exported_files=[json_report.filename, pdf_report.filename, excel_report.filename, "manifest.json"],
            checksums={
                json_report.filename: json_report.checksum,
                pdf_report.filename: pdf_report.checksum,
                excel_report.filename: excel_report.checksum
            },
            generated_timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        manifest_content = manifest.model_dump_json(indent=2).encode('utf-8')
        manifest_checksum = hashlib.sha256(manifest_content).hexdigest()
        manifest.checksums["manifest.json"] = manifest_checksum
        
        # Re-dump with its own checksum
        manifest_content = manifest.model_dump_json(indent=2).encode('utf-8')
        
        # 3. Create ZIP archive in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(json_report.filename, json_report.content)
            zip_file.writestr(pdf_report.filename, pdf_report.content)
            zip_file.writestr(excel_report.filename, excel_report.content)
            zip_file.writestr("manifest.json", manifest_content)
            
        zip_content = zip_buffer.getvalue()
        zip_checksum = hashlib.sha256(zip_content).hexdigest()
        
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        filename = f"Export_{context.configuration.configuration_id}_{date_str}.zip"
        
        return ExportReport(
            export_format=ExportFormat.ZIP,
            filename=filename,
            mime_type="application/zip",
            checksum=zip_checksum,
            file_size=len(zip_content),
            generation_time_ms=0.0,
            success=True,
            content=zip_content
        )
