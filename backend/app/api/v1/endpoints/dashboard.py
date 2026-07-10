"""Dashboard metrics endpoint."""
from fastapi import APIRouter, Depends
from app.api.v1.dependencies import get_store
from app.services.store import BaseConfigurationStore
from app.schemas.api.v1.responses import APISuccessEnvelope
from datetime import datetime, timezone

router = APIRouter(tags=["Dashboard"])


@router.get(
    "/metrics",
    response_model=APISuccessEnvelope,
    summary="Dashboard KPI metrics",
    description="Returns customer-facing configuration metrics for the dashboard.",
)
async def get_dashboard_metrics(store: BaseConfigurationStore = Depends(get_store)):
    if hasattr(store, "get_dashboard_metrics_async"):
        metrics = await store.get_dashboard_metrics_async()
    else:
        # Fallback for InMemoryStore
        configs = store.list(limit=10000, offset=0)
        completed = [c for c in configs if str(c.status) in ("QUOTED", "EXPORTED")]
        totals = []
        for c in completed:
            if c.pricing_summary:
                try:
                    totals.append(float(c.pricing_summary.total_after_tax))
                except Exception:
                    pass
        metrics = {
            "total_configurations": len(configs),
            "completed_quotes": len(completed),
            "configurations_on_hold": len(configs) - len(completed),
            "average_quote_value": round(sum(totals) / len(totals), 2) if totals else 0.0,
        }
    return APISuccessEnvelope(
        success=True,
        data=metrics,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
