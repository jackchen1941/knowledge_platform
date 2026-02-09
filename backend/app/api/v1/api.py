"""
API Router Configuration

Main API router that includes all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    permissions,
    roles,
    knowledge,
    categories,
    tags,
    search,
    import_export,
    analytics,
    attachments,
    knowledge_graph,
    backup,
    import_adapters,
    sync,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(attachments.router, prefix="", tags=["attachments"])  # No prefix as routes are defined in the router
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(import_export.router, prefix="/import-export", tags=["import-export"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(knowledge_graph.router, prefix="", tags=["knowledge-graph"])  # No prefix as routes include their own
api_router.include_router(backup.router, prefix="", tags=["backup"])  # No prefix as routes include their own
api_router.include_router(import_adapters.router, prefix="/import-adapters", tags=["import-adapters"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])