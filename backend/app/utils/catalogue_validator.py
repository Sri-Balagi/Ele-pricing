"""
Catalogue Validator.

Validates the integrity of the product domain catalogue after JSON data is loaded.
Ensures referential integrity, catches duplicates, and flags orphans.
"""

import logging
from typing import Any, Dict, List, Set
from pydantic import ValidationError

from app.core.constants import DataFile
from app.utils.data_loader import DataLoader
from app.models.domain import (
    CatalogMetadata,
    ElevatorCategory,
    FeatureGroup,
    Feature,
    FeatureOption,
    Component,
    FeatureComponentMapping,
    Dependency,
)

logger = logging.getLogger(__name__)


class CatalogueValidationException(Exception):
    """Raised when the catalogue contains semantic integrity errors."""

    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Catalogue validation failed with {len(errors)} errors:\n- " + "\n- ".join(errors))


class CatalogueValidator:
    """
    Validates domain logic and referential integrity across all loaded JSON files.
    """

    def __init__(self, loader: DataLoader):
        self.loader = loader
        self.errors: List[str] = []

        self._categories: Dict[str, Any] = {}
        self._feature_groups: Dict[str, Any] = {}
        self._features: Dict[str, Any] = {}
        self._feature_options: Dict[str, Any] = {}
        self._components: Dict[str, Any] = {}
        self._mappings: Dict[str, Any] = {}
        self._dependencies: Dict[str, Any] = {}

    def _load_data(self) -> None:
        """Loads data from the DataLoader (assumes basic JSON validity has passed)."""
        # Load raw dicts/lists
        cat_raw = self.loader.load(DataFile.CATEGORIES.value)
        grp_raw = self.loader.load(DataFile.FEATURE_GROUPS.value)
        feat_raw = self.loader.load(DataFile.FEATURES.value)
        opt_raw = self.loader.load(DataFile.FEATURE_OPTIONS.value)
        comp_raw = self.loader.load(DataFile.COMPONENTS.value)
        map_raw = self.loader.load(DataFile.FEATURE_MAPPINGS.value)
        dep_raw = self.loader.load(DataFile.DEPENDENCIES.value)

        # Build dictionaries keyed by ID to easily check duplicates and existence
        def build_dict(data_list: List[Dict[str, Any]], entity_name: str) -> Dict[str, Any]:
            result = {}
            for item in data_list:
                item_id = item.get("id")
                if not item_id:
                    self.errors.append(f"Missing 'id' in a {entity_name} record.")
                    continue
                if item_id in result:
                    self.errors.append(f"Duplicate ID found for {entity_name}: {item_id}")
                else:
                    result[item_id] = item
            return result

        self._categories = build_dict(cat_raw, "ElevatorCategory")
        self._feature_groups = build_dict(grp_raw, "FeatureGroup")
        self._features = build_dict(feat_raw, "Feature")
        self._feature_options = build_dict(opt_raw, "FeatureOption")
        self._components = build_dict(comp_raw, "Component")
        self._mappings = build_dict(map_raw, "FeatureComponentMapping")
        self._dependencies = build_dict(dep_raw, "Dependency")

    def _validate_pydantic_schemas(self) -> None:
        """Ensure all loaded items pass Pydantic schema validation."""
        def validate_dict(model, data_dict: Dict[str, Any], entity_name: str) -> None:
            for item_id, item in data_dict.items():
                try:
                    model(**item)
                except ValidationError as exc:
                    self.errors.append(f"Schema validation failed for {entity_name} '{item_id}': {exc}")

        # Metadata is a single object, not a list of dicts.
        meta_raw = self.loader.load(DataFile.CATALOG_METADATA.value)
        if isinstance(meta_raw, list) and len(meta_raw) > 0:
            try:
                CatalogMetadata(**meta_raw[0])
            except ValidationError as exc:
                self.errors.append(f"Schema validation failed for CatalogMetadata: {exc}")
        
        validate_dict(ElevatorCategory, self._categories, "ElevatorCategory")
        validate_dict(FeatureGroup, self._feature_groups, "FeatureGroup")
        validate_dict(Feature, self._features, "Feature")
        validate_dict(FeatureOption, self._feature_options, "FeatureOption")
        validate_dict(Component, self._components, "Component")
        validate_dict(FeatureComponentMapping, self._mappings, "FeatureComponentMapping")
        validate_dict(Dependency, self._dependencies, "Dependency")

    def _validate_references(self) -> None:
        """Check FKs and relationships."""
        
        # Track usage to find orphans
        used_groups: Set[str] = set()
        used_categories: Set[str] = set()
        used_features: Set[str] = set()
        used_options: Set[str] = set()
        used_components: Set[str] = set()

        # Features -> Category & Group
        for f_id, f in self._features.items():
            cat_id = f.get("category_id")
            if cat_id not in self._categories:
                self.errors.append(f"Feature '{f_id}' references unknown category_id: {cat_id}")
            else:
                used_categories.add(cat_id)
                if not self._categories[cat_id].get("active", True):
                    self.errors.append(f"Feature '{f_id}' references inactive category_id: {cat_id}")

            grp_id = f.get("group_id")
            if grp_id not in self._feature_groups:
                self.errors.append(f"Feature '{f_id}' references unknown group_id: {grp_id}")
            else:
                used_groups.add(grp_id)

        # FeatureOptions -> Feature
        for opt_id, opt in self._feature_options.items():
            f_id = opt.get("feature_id")
            if f_id not in self._features:
                self.errors.append(f"FeatureOption '{opt_id}' references unknown feature_id: {f_id}")
            else:
                used_features.add(f_id)
                if not self._features[f_id].get("active", True):
                    self.errors.append(f"FeatureOption '{opt_id}' references inactive feature_id: {f_id}")

        # FeatureComponentMapping -> FeatureOption & Component
        for m_id, m in self._mappings.items():
            opt_id = m.get("feature_option_id")
            if opt_id not in self._feature_options:
                self.errors.append(f"Mapping '{m_id}' references unknown feature_option_id: {opt_id}")
            else:
                used_options.add(opt_id)

            comp_id = m.get("component_id")
            if comp_id not in self._components:
                self.errors.append(f"Mapping '{m_id}' references unknown component_id: {comp_id}")
            else:
                used_components.add(comp_id)

        # Dependencies -> Source & Target
        for d_id, d in self._dependencies.items():
            src_id = d.get("source_id")
            tgt_id = d.get("target_id")

            if src_id not in self._components and src_id not in self._feature_options:
                self.errors.append(f"Dependency '{d_id}' references unknown source_id: {src_id}")
            else:
                if src_id in self._components:
                    used_components.add(src_id)
                if src_id in self._feature_options:
                    used_options.add(src_id)

            if tgt_id not in self._components and tgt_id not in self._feature_options:
                self.errors.append(f"Dependency '{d_id}' references unknown target_id: {tgt_id}")
            else:
                if tgt_id in self._components:
                    used_components.add(tgt_id)
                if tgt_id in self._feature_options:
                    used_options.add(tgt_id)

        # Orphans (Warning log only, not a hard error unless we want strict checking)
        orphaned_features = set(self._features.keys()) - used_features
        if orphaned_features:
            logger.warning("Found %d orphaned Features with no FeatureOptions.", len(orphaned_features))
        
        orphaned_components = set(self._components.keys()) - used_components
        if orphaned_components:
            logger.warning("Found %d orphaned Components with no mappings or dependencies.", len(orphaned_components))

    def validate(self) -> None:
        """
        Run all semantic validations.
        Raises CatalogueValidationException if any errors are found.
        """
        logger.info("Starting Catalogue Integrity Validation...")
        self.errors.clear()
        
        try:
            self._load_data()
        except Exception as e:
            self.errors.append(f"Failed to load data for validation: {str(e)}")
            raise CatalogueValidationException(self.errors)

        if not self.errors:
            self._validate_pydantic_schemas()
        
        if not self.errors:
            self._validate_references()

        if self.errors:
            logger.error("Catalogue validation failed with %d errors.", len(self.errors))
            for error in self.errors:
                logger.error(" - %s", error)
            raise CatalogueValidationException(self.errors)
        
        logger.info("Catalogue validation passed successfully.")
