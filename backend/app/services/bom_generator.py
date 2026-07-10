from typing import Dict, List, Any
from app.models.domain import Configuration, BillOfMaterials, BOMItem, BOMOrigin, ProductCatalogue

class BOMGenerator:
    """
    Service responsible for generating the Bill of Materials structure.
    Strictly handles structure, quantity, and manufacturing traceability.
    NEVER populates unit_cost (owned by Pricing Engine).
    """
    
    def __init__(self, catalogue: ProductCatalogue):
        self.catalogue = catalogue
        
    def generate(self, configuration: Configuration) -> BillOfMaterials:
        items: List[BOMItem] = []
        
        # Fast lookup for active mappings
        active_mappings = [m for m in self.catalogue.mappings if m.active]
        
        # Build lookup for mutations (to track engine additions)
        mutation_lookup: Dict[str, str] = {}
        for mutation in configuration.mutations:
            if mutation.mutation_type == "ADDED":
                mutation_lookup[mutation.entity_id] = mutation.source_engine
                
        # Build lookup for component names
        comp_names: Dict[str, str] = {c.id: c.name for c in self.catalogue.components}
        
        # Build BOM items from resolved components
        for comp_id in configuration.resolved_components:
            # 1. Check Feature Mappings
            matched_mapping = None
            for mapping in active_mappings:
                if mapping.component_id == comp_id and mapping.feature_option_id in configuration.selected_feature_options:
                    matched_mapping = mapping
                    break
            
            if matched_mapping:
                items.append(BOMItem(
                    component_id=comp_id,
                    component_name=comp_names.get(comp_id, "Unknown Component"),
                    quantity=matched_mapping.quantity,
                    source_feature_option_id=matched_mapping.feature_option_id,
                    reason="Feature Mapping",
                    origin_type=BOMOrigin.FEATURE,
                    unit_cost=None,
                    pricing_record_id=None
                ))
                continue
                
            # 2. Check Mutations (Rule or Dependency Engine)
            source_engine = mutation_lookup.get(comp_id)
            if source_engine == "RULE_ENGINE":
                items.append(BOMItem(
                    component_id=comp_id,
                    component_name=comp_names.get(comp_id, "Unknown Component"),
                    quantity=1,
                    source_feature_option_id=None,
                    reason="Rule Engine",
                    origin_type=BOMOrigin.RULE,
                    unit_cost=None,
                    pricing_record_id=None
                ))
            elif source_engine == "DEPENDENCY_ENGINE":
                items.append(BOMItem(
                    component_id=comp_id,
                    component_name=comp_names.get(comp_id, "Unknown Component"),
                    quantity=1,
                    source_feature_option_id=None,
                    reason="Dependency Resolution",
                    origin_type=BOMOrigin.DEPENDENCY,
                    unit_cost=None,
                    pricing_record_id=None
                ))
            else:
                # 3. Manual Override (Fallback)
                items.append(BOMItem(
                    component_id=comp_id,
                    component_name=comp_names.get(comp_id, "Unknown Component"),
                    quantity=1,
                    source_feature_option_id=None,
                    reason="Manual Override",
                    origin_type=BOMOrigin.MANUAL,
                    unit_cost=None,
                    pricing_record_id=None
                ))
                
        return BillOfMaterials(
            items=items,
            total_components=sum(item.quantity for item in items)
        )
