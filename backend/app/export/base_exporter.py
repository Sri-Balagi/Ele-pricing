from abc import ABC, abstractmethod
from app.models.domain import ExportContext, ExportReport

class BaseExporter(ABC):
    """
    Abstract interface for all Export services.
    Exporters are stateless Formatters. They NEVER mutate Configuration.
    """
    
    @abstractmethod
    def export(self, context: ExportContext) -> ExportReport:
        """
        Generate the export format based on the finalized configuration.
        """
        pass
