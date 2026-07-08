from typing import Dict, Type
from app.core.constants import ExportFormat
from app.export.base_exporter import BaseExporter

class ExporterRegistry:
    """
    Registry for managing available export formats.
    Maintains a mapping of ExportFormat -> BaseExporter instance.
    """
    
    def __init__(self):
        self._exporters: Dict[ExportFormat, BaseExporter] = {}
        
    def register(self, format_type: ExportFormat, exporter: BaseExporter) -> None:
        """Register an exporter for a specific format."""
        self._exporters[format_type] = exporter
        
    def get_exporter(self, format_type: ExportFormat) -> BaseExporter:
        """Retrieve an exporter instance for the given format."""
        if format_type not in self._exporters:
            raise ValueError(f"No exporter registered for format: {format_type}")
        return self._exporters[format_type]
