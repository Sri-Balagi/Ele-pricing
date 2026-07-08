# Authentication Integration Point

This package `app/api/auth` is reserved for a future Authentication integration (e.g., OAuth2, JWT verification). 

As per the architectural constraints for Milestone 5, **do not implement authentication here**. This README serves only to document the boundary.

When auth is implemented:
1. Add FastAPI `Security` dependencies here.
2. Inject them into `router.py` or directly onto secured endpoints.
3. Map identities to `Configuration` owners if required.
