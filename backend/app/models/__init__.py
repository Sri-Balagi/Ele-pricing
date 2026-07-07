"""
Domain models package.

Contains internal Pydantic models representing business entities.

IMPORTANT: Models in this package are NEVER exposed directly through the API.
           API schemas live in app/schemas/. This separation enforces the
           API ↔ domain boundary.

Milestone 1 will add:
  - Component model
  - Feature model

Later milestones will add:
  - Rule model
  - DependencyRelationship model
  - PricingEntry model
  - Configuration model
"""
