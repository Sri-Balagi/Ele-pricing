from app.models.domain import (
    BillOfMaterials,
    BOMItem,
    BOMOrigin,
    Configuration,
    ProductCatalogue,
)


class BOMGenerator:
    """
    Service responsible for generating the Bill of Materials structure.
    Strictly handles structure, quantity, and manufacturing traceability.
    NEVER populates unit_cost (owned by Pricing Engine).
    """

    BASE_COMPONENTS_MAP = {
        "CAT-A": ["COMP-BASE-A-MOTOR", "COMP-BASE-A-CABIN", "COMP-BASE-A-CTRL", "COMP-BASE-A-DOOR"],
        "CAT-B": ["COMP-BASE-B-MOTOR", "COMP-BASE-B-CABIN", "COMP-BASE-B-CTRL", "COMP-BASE-B-DOOR"],
        "CAT-C": ["COMP-BASE-C-MOTOR", "COMP-BASE-C-CABIN", "COMP-BASE-C-CTRL", "COMP-BASE-C-DOOR", "COMP-BASE-C-AERO"]
    }

    def __init__(self, catalogue: ProductCatalogue):
        self.catalogue = catalogue

    def generate(self, configuration: Configuration) -> BillOfMaterials:
        items: list[BOMItem] = []

        # Fast lookup for active mappings
        active_mappings = [m for m in self.catalogue.mappings if m.active]

        # Build lookup for mutations (to track engine additions)
        mutation_lookup: dict[str, str] = {}
        for mutation in configuration.mutations:
            if mutation.mutation_type == "ADDED":
                mutation_lookup[mutation.entity_id] = mutation.source_engine

        # Build lookup for component names
        comp_names: dict[str, str] = {c.id: c.name for c in self.catalogue.components}

        # Inject Base Components
        category = configuration.selected_category
        base_comps = self.BASE_COMPONENTS_MAP.get(category, [])
        for comp_id in base_comps:
            items.append(
                BOMItem(
                    component_id=comp_id,
                    component_name=comp_names.get(comp_id, "Base Build Component"),
                    quantity=1,
                    source_feature_option_id=None,
                    reason="Base Build Component",
                    origin_type=BOMOrigin.BASE,
                    unit_cost=None,
                    pricing_record_id=None,
                )
            )

        # Build BOM items from resolved components
        for comp_id in configuration.resolved_components:
            # 1. Check Feature Mappings
            matched_mapping = None
            for mapping in active_mappings:
                if (
                    mapping.component_id == comp_id
                    and mapping.feature_option_id
                    in configuration.selected_feature_options
                ):
                    matched_mapping = mapping
                    break

            if matched_mapping:
                items.append(
                    BOMItem(
                        component_id=comp_id,
                        component_name=comp_names.get(comp_id, "Unknown Component"),
                        quantity=matched_mapping.quantity,
                        source_feature_option_id=matched_mapping.feature_option_id,
                        reason="Feature Mapping",
                        origin_type=BOMOrigin.FEATURE,
                        unit_cost=None,
                        pricing_record_id=None,
                    )
                )
                continue

            # 2. Check Mutations (Rule or Dependency Engine)
            source_engine = mutation_lookup.get(comp_id)
            if source_engine == "RULE_ENGINE":
                items.append(
                    BOMItem(
                        component_id=comp_id,
                        component_name=comp_names.get(comp_id, "Unknown Component"),
                        quantity=1,
                        source_feature_option_id=None,
                        reason="Rule Engine",
                        origin_type=BOMOrigin.RULE,
                        unit_cost=None,
                        pricing_record_id=None,
                    )
                )
            elif source_engine == "DEPENDENCY_ENGINE":
                items.append(
                    BOMItem(
                        component_id=comp_id,
                        component_name=comp_names.get(comp_id, "Unknown Component"),
                        quantity=1,
                        source_feature_option_id=None,
                        reason="Dependency Resolution",
                        origin_type=BOMOrigin.DEPENDENCY,
                        unit_cost=None,
                        pricing_record_id=None,
                    )
                )
            else:
                # 3. Manual Override (Fallback)
                items.append(
                    BOMItem(
                        component_id=comp_id,
                        component_name=comp_names.get(comp_id, "Unknown Component"),
                        quantity=1,
                        source_feature_option_id=None,
                        reason="Manual Override",
                        origin_type=BOMOrigin.MANUAL,
                        unit_cost=None,
                        pricing_record_id=None,
                    )
                )

        return BillOfMaterials(
            items=items, total_components=sum(item.quantity for item in items)
        )
