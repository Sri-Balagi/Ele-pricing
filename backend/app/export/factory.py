from app.core.constants import ExportFormat
from app.export.base_exporter import BaseExporter
from app.export.registry import ExporterRegistry

class ExportFactory:
    """
    Factory responsible solely for resolving the correct BaseExporter 
    from the ExporterRegistry based on ExportFormat.
    """
    
    def __init__(self, registry: ExporterRegistry):
        self._registry = registry
        
    def create(self, format_type: ExportFormat) -> BaseExporter:
        """
        Creates/Retrieves the correct exporter instance for the given format.
        Delegates completely to the registry to avoid if/else logic.
        """
        return self._registry.get_exporter(format_type)
