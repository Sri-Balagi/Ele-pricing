"""
Master APIRouter for API version 1.

All v1 endpoint routers are included here.
Future milestones add sub-routers to this file — no other file changes needed.

Pattern for adding a new milestone router:
    from app.api.v1.endpoints import components
    router.include_router(
        components.router,
        prefix="/components",
        tags=["Components"],
    )
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health

router = APIRouter()

# ── v1 Endpoints ──────────────────────────────────────────────────────────────
router.include_router(health.router)

# ── Future Milestone Routers (uncomment when implemented) ─────────────────────
# from app.api.v1.endpoints import components
# router.include_router(components.router, prefix="/components", tags=["Components"])

from app.api.v1.endpoints import configuration
router.include_router(configuration.router, prefix="/configurations", tags=["Configuration"])

from app.api.v1.endpoints import system
router.include_router(system.router, prefix="/system", tags=["System"])

# from app.api.v1.endpoints import pricing
# router.include_router(pricing.router, prefix="/pricing", tags=["Pricing"])
