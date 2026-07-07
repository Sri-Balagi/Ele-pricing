"""
Services package — business logic orchestration layer.

Layer contract:
  - Services receive domain inputs and coordinate repositories + engines.
  - Services NEVER import from app/api/ (no circular deps).
  - API routes NEVER bypass services to access repositories directly.

Milestone 1 will add:
  - ComponentService
  - FeatureService

Later milestones will add:
  - ConfigurationService
  - DependencyService
  - PricingService
"""
