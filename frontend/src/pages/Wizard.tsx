import React, { useState, useEffect, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useSearchParams, useNavigate, useBlocker } from "react-router-dom";
import { configurationApi } from "@/api";
import { catalogueApi } from "@/api/catalogue";
import { toast } from "sonner";
import {
  Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter,
} from "@/components/ui/card";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { CheckCircle2, Circle, Loader2, RefreshCw, AlertCircle, Save, AlertTriangle } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const NUMERIC_INPUT_FEATURES = new Set(["FEAT-A-STOPS", "FEAT-B-STOPS", "FEAT-C-STOPS", "FEAT-D-STOPS", "FEAT-STOPS"]);

export default function Wizard() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const editConfigId = searchParams.get("edit");
  const isEditMode = !!editConfigId;

  const [activeConfigId, setActiveConfigId] = useState<string | null>(null);
  const [projectName, setProjectName] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [consentGiven, setConsentGiven] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [featureSelections, setFeatureSelections] = useState<Record<string, string | string[]>>({});
  const [stopsError, setStopsError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [draftLoaded, setDraftLoaded] = useState(false);

  const draftKey = `wizard_draft_${editConfigId || 'new'}`;

  // ── Local Storage Draft Restoration ──
  useEffect(() => {
    const draftStr = localStorage.getItem(draftKey);
    if (draftStr) {
      try {
        const draft = JSON.parse(draftStr);
        setActiveConfigId(draft.activeConfigId || null);
        setProjectName(draft.projectName || "");
        setCustomerName(draft.customerName || "");
        setSelectedCategory(draft.selectedCategory || "");
        setFeatureSelections(draft.featureSelections || {});
        setStopsError(draft.stopsError || null);
        setIsDirty(true);
      } catch (e) {
        // ignore
      }
    }
    setDraftLoaded(true);
  }, [draftKey]);

  // Save draft whenever state changes and isDirty is true
  useEffect(() => {
    if (draftLoaded && isDirty) {
      localStorage.setItem(draftKey, JSON.stringify({
        activeConfigId,
        projectName,
        customerName,
        selectedCategory,
        featureSelections,
        stopsError
      }));
    }
  }, [draftLoaded, isDirty, activeConfigId, projectName, customerName, selectedCategory, featureSelections, stopsError, draftKey]);

  // Load existing config if in edit mode
  const { data: existingConfigEnv, isLoading: loadingConfig } = useQuery({
    queryKey: ["configurations", editConfigId],
    queryFn: () => configurationApi.get(editConfigId!),
    enabled: isEditMode,
  });

  useEffect(() => {
    if (draftLoaded && isEditMode && existingConfigEnv?.configuration_id && !isDirty) {
      const config = existingConfigEnv;
      setActiveConfigId(config.configuration_id);
      setProjectName(config.project_name || "");
      setCustomerName(config.customer_name || "");
      setSelectedCategory(config.selected_category || "");
      
      const newSelections: Record<string, string | string[]> = {};
      if (config.selected_feature_options) {
        config.selected_feature_options.forEach((optId: string) => {
          // If it's a STOPS option
          if (optId.startsWith("STOPS-")) {
            // Find which stops feature belongs to this category
            const featureId = `FEAT-${config.selected_category.split('-')[1]}-STOPS`;
            newSelections[featureId] = optId;
          } else {
            // We need to reverse lookup feature ID from option ID. For now we assume options have format OPT-{CAT}-{FEAT}
            // but this is tricky without catalogue data. Actually, the easiest way is to let the user select it again, 
            // but for a true edit we need to map option -> feature.
            // Let's rely on catalogue query completing first to map it.
          }
        });
      }
      // Wait for catalogue to populate feature selections correctly
    }
  }, [isEditMode, existingConfigEnv, draftLoaded, isDirty]);

  // ── Catalogue queries ────────────────────────────────────────────────────────
  const { data: categories = [], isLoading: loadingCats } = useQuery({
    queryKey: ["catalogue", "categories"],
    queryFn: catalogueApi.getCategories,
  });

  const { data: features = [], isLoading: loadingFeatures } = useQuery({
    queryKey: ["catalogue", "features"],
    queryFn: catalogueApi.getFeatures,
  });

  const { data: featureOptions = [], isLoading: loadingOptions } = useQuery({
    queryKey: ["catalogue", "feature-options"],
    queryFn: catalogueApi.getFeatureOptions,
  });

  const { data: dependencies = [], isLoading: loadingDeps } = useQuery({
    queryKey: ["catalogue", "dependencies"],
    queryFn: catalogueApi.getDependencies,
  });

  // Populate featureSelections once catalogue is loaded
  useEffect(() => {
    if (draftLoaded && isEditMode && existingConfigEnv?.configuration_id && !loadingFeatures && !loadingOptions && !isDirty) {
      const config = existingConfigEnv;
      const opts = featureOptions as any[];
      const feats = features as any[];
      const newSelections: Record<string, string | string[]> = {};
      
      if (config.selected_feature_options) {
        config.selected_feature_options.forEach((optId: string) => {
          if (optId.startsWith("STOPS-")) {
            const catLetter = config.selected_category.split('-')[1];
            newSelections[`FEAT-${catLetter}-STOPS`] = optId;
          } else {
            const optionDef = opts.find(o => o.id === optId);
            if (optionDef) {
              const featureDef = feats.find(f => f.id === optionDef.feature_id);
              if (featureDef?.metadata?.multi_select) {
                if (!newSelections[optionDef.feature_id]) {
                  newSelections[optionDef.feature_id] = [];
                }
                (newSelections[optionDef.feature_id] as string[]).push(optId);
              } else {
                newSelections[optionDef.feature_id] = optId;
              }
            }
          }
        });
      }
      setFeatureSelections(newSelections);
      setIsDirty(false); // Clean on load
    }
  }, [isEditMode, existingConfigEnv, loadingFeatures, loadingOptions, features, featureOptions, draftLoaded, isDirty]);

  const catalogueLoading = loadingCats || loadingFeatures || loadingOptions || loadingConfig || loadingDeps;
  
  const getIncompatibilities = (optionId: string) => {
    if (selectedCategory !== "CAT-B" && selectedCategory !== "CAT-D") return null;
    const selectedIds = Object.values(featureSelections).flat().filter(Boolean) as string[];
    
    // Check EXCLUDES
    const conflicts = (dependencies as any[]).filter(d => d.dependency_type === "EXCLUDES").filter(d => {
      if (d.target_id === optionId && selectedIds.includes(d.source_id)) return true;
      if (d.source_id === optionId && selectedIds.includes(d.target_id)) return true;
      return false;
    });

    if (conflicts.length > 0) {
      const messages = conflicts.map(c => {
        const conflictingId = c.source_id === optionId ? c.target_id : c.source_id;
        const conflictOpt = (featureOptions as any[]).find(o => o.id === conflictingId);
        if (conflictOpt) {
          const conflictFeat = (features as any[]).find(f => f.id === conflictOpt.feature_id);
          return conflictFeat ? `${conflictFeat.name} (${conflictOpt.display_name})` : conflictOpt.display_name;
        }
        return "Unknown selection";
      });
      return `Incompatible with: ${messages.join(" and ")}`;
    }

    // Check REQUIRES
    const optToTest = (featureOptions as any[]).find(o => o.id === optionId);
    if (!optToTest) return null;

    const requiresConflicts = (dependencies as any[]).filter(d => d.dependency_type === "REQUIRES").filter(d => {
      if (selectedIds.includes(d.source_id)) {
        const requiredOpt = (featureOptions as any[]).find(o => o.id === d.target_id);
        if (requiredOpt && requiredOpt.feature_id === optToTest.feature_id && optionId !== d.target_id) {
          return true; // Conflict: A required option for this feature must be selected instead
        }
      }
      return false;
    });

    if (requiresConflicts.length > 0) {
      const messages = requiresConflicts.map(c => {
        const sourceOpt = (featureOptions as any[]).find(o => o.id === c.source_id);
        const targetOpt = (featureOptions as any[]).find(o => o.id === c.target_id);
        if (sourceOpt && targetOpt) {
          const sourceFeat = (features as any[]).find(f => f.id === sourceOpt.feature_id);
          const featName = sourceFeat ? sourceFeat.name : "A selected option";
          return `Blocked: ${featName} (${sourceOpt.display_name}) requires "${targetOpt.display_name}"`;
        }
        return "Blocked by a required dependency";
      });
      return messages.join(". ");
    }

    return null;
  };

  // Filter features to only show ones for the selected category
  const activeFeatures = (features as any[]).filter(f => f.category_id === selectedCategory);

  // Group options by feature_id
  const optionsByFeature: Record<string, typeof featureOptions> = {};
  (featureOptions as any[]).forEach((opt) => {
    if (!optionsByFeature[opt.feature_id]) optionsByFeature[opt.feature_id] = [];
    optionsByFeature[opt.feature_id].push(opt);
  });

  // Active category object (for metadata like max_stops)
  const activeCategoryObj = (categories as any[]).find((c) => c.id === selectedCategory);
  const maxStops: number | null = activeCategoryObj?.metadata?.max_stops ?? null;

  // ── Dynamic Compatibility Toasts ──────────────────────────────────────────────
  const prevIncompatibilities = useRef<Record<string, string | null>>({});
  const activeToasts = useRef<Record<string, string | number>>({});
  const initialLoadDone = useRef(false);
  const prevCategory = useRef(selectedCategory);

  useEffect(() => {
    if (prevCategory.current !== selectedCategory) {
      initialLoadDone.current = false;
      prevCategory.current = selectedCategory;
      prevIncompatibilities.current = {};
    }

    if ((selectedCategory !== "CAT-B" && selectedCategory !== "CAT-D") || !featureOptions) return;

    const currentIncompatibilities: Record<string, string | null> = {};
    (featureOptions as any[]).forEach(opt => {
      currentIncompatibilities[opt.id] = getIncompatibilities(opt.id);
    });

    if (!initialLoadDone.current) {
      prevIncompatibilities.current = currentIncompatibilities;
      initialLoadDone.current = true;
      return;
    }

    const newRedToasts: { id: string, msg: string }[] = [];
    const newGreenToasts: { id: string, msg: string }[] = [];

    (featureOptions as any[]).forEach(opt => {
      const inc = currentIncompatibilities[opt.id];
      const prevInc = prevIncompatibilities.current[opt.id];
      
      const feature = (features as any[]).find(f => f.id === opt.feature_id);
      const featureName = feature ? feature.name : "Unknown Feature";
      const fullName = `${featureName} (${opt.display_name})`;
      
      if (inc !== prevInc) {
        if (inc) {
          if (!prevInc) {
            newRedToasts.push({ id: opt.id, msg: `"${fullName}" is now incompatible: ${inc}` });
          } else {
            newRedToasts.push({ id: opt.id, msg: `"${fullName}" incompatibility updated: ${inc}` });
          }
        } else if (prevInc) {
          newGreenToasts.push({ id: opt.id, msg: `"${fullName}" is now compatible and available for selection.` });
        }
      }
    });

    newRedToasts.forEach(({ id, msg }) => {
      if (activeToasts.current[id]) {
        toast.dismiss(activeToasts.current[id]);
      }
      const newId = `${id}-${Date.now()}`;
      activeToasts.current[id] = newId;
      setTimeout(() => toast.error(msg, { id: newId, duration: 6000 }), 300);
    });

    newGreenToasts.forEach(({ id, msg }) => {
      if (activeToasts.current[id]) {
        toast.dismiss(activeToasts.current[id]);
      }
      const newId = `${id}-${Date.now()}`;
      activeToasts.current[id] = newId;
      setTimeout(() => toast.success(msg, { id: newId, duration: 6000 }), 300);
    });

    prevIncompatibilities.current = currentIncompatibilities;
  }, [featureSelections, featureOptions, selectedCategory]);

  // ── Dirty / unsaved guard ────────────────────────────────────────────────────
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (isDirty) { 
        e.preventDefault(); 
        e.returnValue = ""; 
      }
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [isDirty]);

  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty && (currentLocation.pathname !== nextLocation.pathname || currentLocation.search !== nextLocation.search)
  );

  // ── Mutations ────────────────────────────────────────────────────────────────
  const createMutation = useMutation({
    mutationFn: configurationApi.create,
    onSuccess: (data: any) => {
      toast.success("Project started! Now select your elevator type.");
      setActiveConfigId(data.configuration_id);
      setIsDirty(false);
    },
    onError: (error: any) => toast.error(error.message || "Failed to start project"),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: { id: string; data: any }) =>
      configurationApi.update(payload.id, payload.data),
    onSuccess: () => {
      toast.success("Configuration saved successfully!");
      setIsDirty(false);
      localStorage.removeItem(draftKey);
      queryClient.invalidateQueries({ queryKey: ["dashboard_metrics"] });
      if (blocker.state === "blocked") {
        blocker.proceed();
      }
    },
    onError: (error: any) => toast.error(error.message || "Failed to update configuration"),
  });

  // ── Handlers ─────────────────────────────────────────────────────────────────
  const handleStartProject = () => {
    if (!projectName.trim()) { toast.error("Please enter a Project Name."); return; }
    
    const custName = customerName.trim();
    if (!custName) {
      toast.error("Please enter a Customer Name.");
      return;
    }
    if (!/^[A-Za-z\s]+$/.test(custName)) {
      toast.error("Customer Name must contain only alphabets and spaces.");
      return;
    }

    createMutation.mutate({
      project_name: projectName.trim(),
      customer_name: custName,
      selected_category: null,
    });
  };

  const handleCategoryChange = (val: string) => {
    setSelectedCategory(val);
    const catLetter = val.split('-')[1];
    
    if (val === "CAT-A") {
      setFeatureSelections({ 
        [`FEAT-A-STOPS`]: "STOPS-2",
        "FEAT-A-CAPACITY": "OPT-A-CAP-630",
        "FEAT-A-SPEED": "OPT-A-SPD-100",
        "FEAT-A-DOOR-TYPE": "OPT-A-DOOR-SO",
        "FEAT-A-CABIN-FINISH": "OPT-A-FIN-SS"
      });
    } else if (val === "CAT-B") {
      setFeatureSelections({ 
        [`FEAT-B-STOPS`]: "STOPS-2", // min stops for CAT-B is 2
        "FEAT-B-CAPACITY": "OPT-B-CAP-630",
        "FEAT-B-SPEED": "OPT-B-SPEED-10",
        "FEAT-B-DOOR-TYPE": "OPT-B-DOOR-SIDE",
        "FEAT-B-CABIN-FINISH": "OPT-B-WALL-SS",
        "FEAT-B-DOOR-DIM": "OPT-B-DIM-900",
        "FEAT-B-FLOORING": "OPT-B-FLOOR-PVC",
        "FEAT-B-CEILING": "OPT-B-CEIL-STD",
        "FEAT-B-HANDRAIL": "OPT-B-RAIL-REAR",
        "FEAT-B-COP": "OPT-B-COP-PUSH",
        "FEAT-B-DEST-CTRL": "OPT-B-DEST-NONE",
        "FEAT-B-DRIVE": "OPT-B-DRIVE-GEARED",
        "FEAT-B-SUSPENSION": "OPT-B-SUSP-ROPE",
        "FEAT-B-CWT-LOC": "OPT-B-CWT-SIDE",
        "FEAT-B-SHAFT": "OPT-B-SHAFT-CONCRETE",
        "FEAT-B-ENERGY-MODE": "OPT-B-NRG-ECO",
        "FEAT-B-GROUP-CTRL": "OPT-B-GRP-SIMP",
        "FEAT-B-PIT-DEPTH": "OPT-B-PIT-STD"
      });
    } else if (val === "CAT-D") {
      setFeatureSelections({ 
        [`FEAT-D-STOPS`]: "STOPS-2",
        "FEAT-D-CAPACITY": "OPT-D-CAP-630",
        "FEAT-D-SPEED": "OPT-D-SPEED-10",
        "FEAT-D-DOOR-TYPE": "OPT-D-DOOR-SIDE",
        "FEAT-D-CABIN-FINISH": "OPT-D-WALL-SS",
        "FEAT-D-DOOR-DIM": "OPT-D-DIM-900",
        "FEAT-D-FLOORING": "OPT-D-FLOOR-PVC",
        "FEAT-D-CEILING": "OPT-D-CEIL-STD",
        "FEAT-D-HANDRAIL": "OPT-D-RAIL-REAR",
        "FEAT-D-COP": "OPT-D-COP-PUSH",
        "FEAT-D-DEST-CTRL": "OPT-D-DEST-NONE",
        "FEAT-D-DRIVE": "OPT-D-DRIVE-GEARED",
        "FEAT-D-SUSPENSION": "OPT-D-SUSP-ROPE",
        "FEAT-D-CWT-LOC": "OPT-D-CWT-SIDE",
        "FEAT-D-SHAFT": "OPT-D-SHAFT-CONCRETE",
        "FEAT-D-ENERGY-MODE": "OPT-D-NRG-ECO",
        "FEAT-D-GROUP-CTRL": "OPT-D-GRP-SIMP",
        "FEAT-D-PIT-DEPTH": "OPT-D-PIT-STD",
        "FEAT-D-MIRROR": "OPT-D-MIRROR-NONE",
        "FEAT-D-KICKPLATE": "OPT-D-KICK-NONE",
        "FEAT-D-BUMPER": "OPT-D-BUMPER-NONE",
        "FEAT-D-DOOR-FINISH": "OPT-D-DOOR-SS",
        "FEAT-D-ARCHITRAVE": "OPT-D-ARCH-NARROW",
        "FEAT-D-THRESHOLD": "OPT-D-THRESH-ALU",
        "FEAT-D-CAR-MAT": "OPT-D-MAT-NONE",
        "FEAT-D-EXT-DISPLAY": "OPT-D-EXT-DOT",
        "FEAT-D-VENTILATION": "OPT-D-VENT-STD",
        "FEAT-D-AIR-PURIFIER": "OPT-D-PURIFY-NONE",
        "FEAT-D-MUSIC": "OPT-D-MUSIC-NONE",
        "FEAT-D-CHIME": "OPT-D-CHIME-STD",
        "FEAT-D-VOICE": "OPT-D-VOICE-NONE",
        "FEAT-D-SANITIZER": "OPT-D-SANI-NONE",
        "FEAT-D-LIGHTING": "OPT-D-LIGHT-COOL",
        "FEAT-D-VIBRATION": "OPT-D-VIBE-STD",
        "FEAT-D-RFID": "OPT-D-RFID-NONE",
        "FEAT-D-FINGERPRINT": "OPT-D-FINGER-NONE",
        "FEAT-D-CAMERA": "OPT-D-CAM-NONE",
        "FEAT-D-VIP-MODE": "OPT-D-VIP-NONE",
        "FEAT-D-ALARM": "OPT-D-ALARM-LOCAL",
        "FEAT-D-PHONE": "OPT-D-PHONE-ANALOG",
        "FEAT-D-ACCESS-CTRL": "OPT-D-ACC-NONE",
        "FEAT-D-EVACUATION": "OPT-D-EVAC-STD",
        "FEAT-D-TOUCHLESS": "OPT-D-TOUCH-NONE",
        "FEAT-D-APP-CALL": "OPT-D-APP-NONE",
        "FEAT-D-IOT": "OPT-D-IOT-BASIC",
        "FEAT-D-DISPLAY-AD": "OPT-D-DISP-NONE",
        "FEAT-D-WIFI": "OPT-D-WIFI-NONE",
        "FEAT-D-REGEN-DRIVE": "OPT-D-REGEN-NONE",
        "FEAT-D-BUTTON-COLOR": "OPT-D-BTN-WHITE",
        "FEAT-D-SEISMIC": "OPT-D-SEISMIC-NONE"
      });
    } else if (val === "CAT-C") {
      setFeatureSelections({
        [`FEAT-C-STOPS`]: "STOPS-2", // min stops for CAT-C is 2
        "FEAT-C-DRIVE-RATING": "OPT-C-DRV-75",
        "FEAT-C-INCLINATION": "OPT-C-INC-0",
        "FEAT-C-LOAD-CLASS": "OPT-C-LOD-STD",
        "FEAT-C-DOOR-PROTECT": "OPT-C-DRP-STD",
        "FEAT-C-CERT-TYPE": [],
        "FEAT-C-CORR-PROT": [],
        "FEAT-C-SHAFT-TYPE": "",
        "FEAT-C-VIB-ISO": "",
        "FEAT-C-FIRE-EVAC": "OPT-C-FIR-NONE",
        "FEAT-C-REMOTE-MON": "OPT-C-MON-NONE"
      });
    } else {
      setFeatureSelections({ [`FEAT-${catLetter}-STOPS`]: "STOPS-2" }); // Set default STOPS to 2
    }
    
    setIsDirty(true);
  };

  const handleDropdownChange = (featureId: string, optionId: string) => {
    const inc = getIncompatibilities(optionId);
    if (inc) {
      toast.error(inc);
      return;
    }

    const requiresRules = (dependencies as any[]).filter(d => d.dependency_type === "REQUIRES" && d.source_id === optionId);
    
    if (requiresRules.length > 0) {
      const updates: Record<string, string> = {};
      const messages: string[] = [];
      
      requiresRules.forEach(rule => {
        const requiredOpt = (featureOptions as any[]).find(o => o.id === rule.target_id);
        if (requiredOpt) {
          const reqFeature = (features as any[]).find(f => f.id === requiredOpt.feature_id);
          const reqFeatureName = reqFeature ? reqFeature.name : "Unknown Feature";
          updates[requiredOpt.feature_id] = requiredOpt.id;
          messages.push(`"${reqFeatureName} (${requiredOpt.display_name})" was auto-selected`);
        }
      });
      
      if (messages.length > 0) {
        toast.info(`${messages.join(" and ")} due to requirement.`);
      }
      
      setFeatureSelections((prev) => ({ ...prev, [featureId]: optionId, ...updates }));
    } else {
      setFeatureSelections((prev) => ({ ...prev, [featureId]: optionId }));
    }
    
    setIsDirty(true);
  };

  const handleCheckboxChange = (featureId: string, optionId: string, checked: boolean) => {
    setFeatureSelections((prev) => {
      const current = prev[featureId];
      const arr = Array.isArray(current) ? current : (current ? [current] : []);
      let nextArr;
      if (checked) {
        nextArr = [...arr, optionId];
      } else {
        nextArr = arr.filter((id) => id !== optionId);
      }
      return { ...prev, [featureId]: nextArr };
    });
    setIsDirty(true);
  };

  const handleStopsChange = (featureId: string, value: string) => {
    setStopsError(null);
    setIsDirty(true);
    const num = parseInt(value, 10);
    if (value === "") {
      setFeatureSelections((prev) => { const next = { ...prev }; delete next[featureId]; return next; });
      return;
    }
    
    // Optimistically update feature selections to allow intermediate invalid states (like '1')
    setFeatureSelections((prev) => ({ ...prev, [featureId]: `STOPS-${num}` }));

    if (isNaN(num) || num < 2) {
      setStopsError("Minimum 2 stops required.");
      return;
    }
    if (maxStops !== null && num > maxStops) {
      setStopsError(`Maximum ${maxStops} stops for ${activeCategoryObj?.name}.`);
      return;
    }
  };

  const handleSaveAll = () => {
    if (!activeConfigId) return;
    if (stopsError) { toast.error("Please fix the Number of Stops before saving."); return; }
    const selectedOptions = Object.values(featureSelections).flat().filter(Boolean) as string[];
    updateMutation.mutate({ 
      id: activeConfigId, 
      data: { 
        project_name: projectName.trim(),
        customer_name: customerName.trim(),
        selected_category: selectedCategory,
        selected_feature_options: selectedOptions 
      } 
    });
  };

  const handleNewSessionClick = () => {
    navigate("/wizard");
  };

  const resetSession = () => {
    setActiveConfigId(null);
    setProjectName("");
    setCustomerName("");
    setSelectedCategory("");
    setProjectName("");
    setFeatureSelections({});
    setStopsError(null);
    setIsDirty(false);
  };

  const completedFeatures = activeFeatures.filter((f) => {
    if (!f.required) return true;
    const selected = featureSelections[f.id];
    if (!selected) return false;
    if (Array.isArray(selected) && selected.length === 0) return false;
    return true;
  });

  // Calculate total cost
  let totalCost = 0;
  const optsArray = featureOptions as any[];
  Object.values(featureSelections).forEach(selectedVal => {
    const ids = Array.isArray(selectedVal) ? selectedVal : [selectedVal];
    ids.forEach(selectedId => {
      if (selectedId && !selectedId.startsWith("STOPS-")) {
        const opt = optsArray.find(o => o.id === selectedId);
        if (opt && opt.price) {
          totalCost += opt.price;
        }
      }
    });
  });

  // Grouping logic for rendering
  let renderGroups: { title?: string, features: any[] }[];

  if (selectedCategory === "CAT-A") {
    const mechNames = ["Load Capacity", "Rated Speed", "Door Opening Type", "Number of Stops"];
    const designNames = ["Cabin Wall Finish"];
    renderGroups = [
      { 
        title: "Mechanical Features", 
        features: mechNames.map(name => activeFeatures.find(f => f.name === name)).filter(Boolean)
      },
      { 
        title: "Design Features", 
        features: designNames.map(name => activeFeatures.find(f => f.name === name)).filter(Boolean)
      }
    ];
  } else if (selectedCategory === "CAT-B" || selectedCategory === "CAT-D") {
    const mechNames = [
      "Load Capacity", "Rated Speed", "Door Opening Type", "Door Dimensions", 
      "Drive System", "Suspension Type", "Counterweight Location", "Shaft Type", 
      "Energy Savings Mode", "Group Control", "Pit Depth", "Destination Control System", 
      "Operating Panel (COP)", "Handrails", "Number of Stops"
    ];
    const designNames = ["Cabin Wall Finish", "Cabin Flooring", "Ceiling Design"];
    
    // CAT-D specific names
    const aestheticNames = [
      "Mirror Configuration", "Kickplate Material", "Bumper Rails", "Door Surface Finish", 
      "Architrave Style", "Sill Material", "Custom Car Mats", "Exterior Indicator"
    ];
    const comfortNames = [
      "Ventilation System", "Air Purifier", "Background Music", "Arrival Chime", 
      "Voice Annunciator", "Hand Sanitizer", "Cabin Lighting", "Anti-Vibration"
    ];
    const securityNames = [
      "RFID Card Reader", "Biometric Scanner", "CCTV Camera", "VIP Priority Mode", 
      "Emergency Alarm", "Intercom System", "Floor Lockout", "Evacuation Mode"
    ];
    const smartNames = [
      "Touchless Buttons", "App Calling", "IoT Maintenance", "In-Cabin Ad Screen", 
      "Wi-Fi Router", "Regenerative Drive", "Button Color", "Seismic Sensor"
    ];

    renderGroups = [
      {
        title: "Mechanical Features",
        features: mechNames.map(name => activeFeatures.find(f => f.name === name)).filter(Boolean)
      },
      {
        title: "Design Features",
        features: designNames.map(name => activeFeatures.find(f => f.name === name)).filter(Boolean)
      }
    ];

    if (selectedCategory === "CAT-D") {
      renderGroups.push(
        {
          title: "Aesthetics & Materials",
          features: aestheticNames.map(name => activeFeatures.find(f => f.name === name)).filter(Boolean)
        },
        {
          title: "Comfort & Environment",
          features: comfortNames.map(name => activeFeatures.find(f => f.name === name)).filter(Boolean)
        },
        {
          title: "Security & Access",
          features: securityNames.map(name => activeFeatures.find(f => f.name === name)).filter(Boolean)
        },
        {
          title: "Smart & Technology",
          features: smartNames.map(name => activeFeatures.find(f => f.name === name)).filter(Boolean)
        }
      );
    }
  } else {
    renderGroups = [{ features: activeFeatures }];
  }


  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-20">
      

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">Configuration Wizard</h1>
            {isEditMode && <Badge variant="secondary" className="bg-blue-100 text-blue-800 border-blue-200">Edit Mode</Badge>}
            {isDirty && <Badge variant="outline" className="text-amber-600 border-amber-200 bg-amber-50">Unsaved Changes</Badge>}
          </div>
          <p className="text-muted-foreground mt-1">
            {activeConfigId ? `Config ID: ${activeConfigId}` : "Configure your elevator step by step."}
          </p>
        </div>
        <Button variant="outline" onClick={handleNewSessionClick}>
          <RefreshCw className="w-4 h-4 mr-2" /> New Session
        </Button>
      </div>

      {/* ── Step 1: Project Details ── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {activeConfigId
              ? <CheckCircle2 className="w-5 h-5 text-green-500" />
              : <Circle className="w-5 h-5 text-muted-foreground" />}
            Step 1 — Project Information
          </CardTitle>
          <CardDescription>Enter a project name to begin tracking this configuration.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="project_name" className="font-semibold">Project Name <span className="text-destructive">*</span></Label>
              <Input
                id="project_name"
                placeholder="e.g. Skyline Towers Phase 1"
                value={projectName}
                onChange={(e) => { setProjectName(e.target.value); setIsDirty(true); }}
                disabled={!!activeConfigId} // Locked after creation and in edit mode
              />
            </div>

            {activeConfigId && (
              <div className="space-y-2">
                <Label className="font-semibold text-muted-foreground">Project ID</Label>
                <div className="h-9 flex items-center px-3 font-mono text-sm bg-muted/30 border rounded-md text-muted-foreground cursor-not-allowed">
                  {activeConfigId}
                </div>
              </div>
            )}

            <div className={`space-y-2 ${activeConfigId ? "md:col-span-2" : ""}`}>
              <Label htmlFor="customer_name" className="font-semibold">Project-in Charge / Customer Name <span className="text-destructive">*</span></Label>
              <Input
                id="customer_name"
                placeholder="e.g. John Doe"
                value={customerName}
                onChange={(e) => { setCustomerName(e.target.value); setIsDirty(true); }}
                disabled={!!activeConfigId} // Locked after creation and in edit mode
              />
            </div>
            
            {!activeConfigId && (
              <div className="md:col-span-2 flex items-start space-x-3 mt-2">
                <Checkbox
                  id="consent"
                  checked={consentGiven}
                  onCheckedChange={(checked) => setConsentGiven(!!checked)}
                />
                <label
                  htmlFor="consent"
                  className="text-sm text-muted-foreground leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 mt-1 cursor-pointer"
                >
                  Creation of this project requires valid customer data. Please check this box to confirm you agree to this data collection.
                </label>
              </div>
            )}
          </div>
        </CardContent>
        {!activeConfigId && (
          <CardFooter>
            <Button onClick={handleStartProject} disabled={!projectName.trim() || !customerName.trim() || !consentGiven || createMutation.isPending} className="ml-auto">
              {createMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Start Project →
            </Button>
          </CardFooter>
        )}
      </Card>

      {/* ── Step 2: Category ── */}
      {activeConfigId && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {selectedCategory
                ? <CheckCircle2 className="w-5 h-5 text-green-500" />
                : <Circle className="w-5 h-5 text-muted-foreground" />}
              Step 2 — Elevator Type
            </CardTitle>
            <CardDescription>Select the elevator category. This determines available features.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="category-select">Elevator Category <span className="text-destructive">*</span></Label>
              {catalogueLoading ? (
                <div className="flex items-center gap-2 text-muted-foreground text-sm h-10">
                  <Loader2 className="w-4 h-4 animate-spin" /> Loading options…
                </div>
              ) : (
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <Select value={selectedCategory} onValueChange={(val) => val && handleCategoryChange(val)}>
                      <SelectTrigger id="category-select" className="w-full">
                        <SelectValue placeholder="— Select elevator type —" />
                      </SelectTrigger>
                      <SelectContent>
                        {(categories as any[]).map((cat) => (
                          <SelectItem key={cat.id} value={cat.id}>
                            <span className="font-medium">{cat.name}</span>
                            <span className="ml-2 text-xs text-muted-foreground">{cat.id}</span>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="w-auto shrink-0 text-right">
                    <Badge variant={selectedCategory ? "default" : "outline"} className={selectedCategory ? "bg-primary" : "text-muted-foreground"}>
                      Base Cost: ${selectedCategory ? ((categories as any[]).find(c => c.id === selectedCategory)?.metadata?.base_cost || 0).toFixed(2) : "0.00"}
                    </Badge>
                  </div>
                </div>
              )}
              {selectedCategory && (
                <p className="text-sm text-muted-foreground mt-2 p-3 bg-muted/50 rounded-md">
                  {activeCategoryObj?.description}
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Step 3: Features ── */}
      {selectedCategory && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                {completedFeatures.length === activeFeatures.length && activeFeatures.length > 0
                  ? <CheckCircle2 className="w-5 h-5 text-green-500" />
                  : <Circle className="w-5 h-5 text-muted-foreground" />}
                Step 3 — Feature Configuration
              </CardTitle>
              <Badge variant="outline">
                {completedFeatures.length}/{activeFeatures.length} selected
              </Badge>
            </div>
            <CardDescription>
              Configure each feature below.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            {catalogueLoading ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" /> Loading features…
              </div>
            ) : (
              renderGroups.map((group, groupIdx) => (
                <div key={groupIdx} className="space-y-5">
                  {group.title && (
                    <div className="mt-8 mb-4 first:mt-0">
                      <h3 className="text-lg font-bold text-primary">{group.title}</h3>
                      <Separator className="mt-2" />
                    </div>
                  )}
                  {group.features.map((feature, idx) => {
                const isNumeric = NUMERIC_INPUT_FEATURES.has(feature.id);
                const opts = optionsByFeature[feature.id] || [];
                const selected = featureSelections[feature.id];
                const isComplete = !feature.required || (!!selected && (!Array.isArray(selected) || selected.length > 0) && !stopsError);
                const stopsRawValue = selected && typeof selected === "string" && selected.startsWith("STOPS-") ? selected.replace("STOPS-", "") : "";

                let numericCost = 0;
                if (isNumeric && stopsRawValue) {
                  const numStops = parseInt(stopsRawValue, 10);
                  if (!isNaN(numStops) && numStops > 0) {
                    if (selectedCategory === "CAT-A") numericCost = Math.max(0, numStops - 2) * 2000;
                    else if (selectedCategory === "CAT-B") numericCost = Math.max(0, numStops - 2) * 3800;
                    else if (selectedCategory === "CAT-D") numericCost = Math.max(0, numStops - 2) * 3800;
                    else if (selectedCategory === "CAT-C") numericCost = Math.max(0, numStops - 2) * 8500;
                  }
                }

                return (
                  <div key={feature.id}>
                    {idx > 0 && <Separator className="mb-5" />}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label htmlFor={`feature-${feature.id}`} className="text-sm font-semibold">
                          {feature.name}
                          {feature.required && <span className="ml-1 text-destructive">*</span>}
                        </Label>
                        {isComplete && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                      </div>
                      <p className="text-xs text-muted-foreground">{feature.description}</p>

                      {isNumeric ? (
                        <div className="flex items-center gap-4">
                          <div className="flex-1 flex items-center gap-3">
                            <Input
                              id={`feature-${feature.id}`}
                              type="number"
                              min={2}
                              max={maxStops ?? undefined}
                              placeholder="Enter number of stops"
                              value={stopsRawValue}
                              onChange={(e) => handleStopsChange(feature.id, e.target.value)}
                              className={stopsError ? "border-destructive focus-visible:ring-destructive" : ""}
                            />
                            {maxStops !== null && (
                              <span className="text-sm text-muted-foreground whitespace-nowrap">
                                Max. No.: <strong>{maxStops}</strong>
                              </span>
                            )}
                          </div>
                          <div className="w-24 shrink-0 text-right">
                            <Badge variant={selected ? "default" : "outline"} className={selected ? "bg-primary" : "text-muted-foreground"}>
                              Cost: ${numericCost.toFixed(2)}
                            </Badge>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center gap-4">
                          <div className="flex-1">
                            {selectedCategory === "CAT-A" && ["FEAT-A-CAPACITY", "FEAT-A-SPEED", "FEAT-A-DOOR-TYPE"].includes(feature.id) ? (
                              <div className="flex h-10 w-full rounded-md border border-input bg-muted px-3 py-2 text-sm ring-offset-background cursor-not-allowed text-muted-foreground items-center">
                                {opts.find((o: any) => o.id === selected)?.display_name || "— Default fixed —"}
                              </div>
                            ) : feature.metadata?.multi_select ? (
                              <div className="flex flex-col gap-3 p-3 bg-muted/30 rounded-md border">
                                {opts.length > 0 ? (
                                  opts.map((opt: any) => {
                                    const isChecked = Array.isArray(selected) && selected.includes(opt.id);
                                    return (
                                      <div key={opt.id} className="flex flex-row items-start space-x-3 space-y-0 p-2">
                                        <Checkbox 
                                          id={`checkbox-${opt.id}`} 
                                          checked={isChecked}
                                          onCheckedChange={(checked) => handleCheckboxChange(feature.id, opt.id, !!checked)}
                                        />
                                        <div className="space-y-1 leading-none w-full flex justify-between">
                                          <div>
                                            <Label htmlFor={`checkbox-${opt.id}`} className="font-medium cursor-pointer">
                                              {opt.display_name}
                                            </Label>
                                            {opt.description && (
                                              <p className="text-xs text-muted-foreground mt-1">{opt.description}</p>
                                            )}
                                          </div>
                                          <span className="text-xs font-semibold text-muted-foreground">
                                            +${(opt.price || 0).toFixed(2)}
                                          </span>
                                        </div>
                                      </div>
                                    )
                                  })
                                ) : (
                                  <span className="text-sm text-muted-foreground">No options available</span>
                                )}
                              </div>
                            ) : (
                              <Select value={(selected as string) || ""} onValueChange={(val) => val && handleDropdownChange(feature.id, val)}>
                                <SelectTrigger id={`feature-${feature.id}`} className="w-full">
                                  {selected ? (
                                    <span className="truncate">
                                      {opts.find((o: any) => o.id === selected)?.display_name || (selected as string)}
                                    </span>
                                  ) : (
                                    <span className="text-muted-foreground truncate">
                                      — Choose {feature.name} —
                                    </span>
                                  )}
                                </SelectTrigger>
                                <SelectContent>
                                  {opts.length > 0 ? (
                                    opts.map((opt: any) => {
                                      const inc = getIncompatibilities(opt.id);
                                      return (
                                        <SelectItem key={opt.id} value={opt.id} className={inc ? "opacity-50 text-muted-foreground" : ""}>
                                          <div className="flex flex-col text-left">
                                            <div className="flex items-center justify-between gap-4">
                                              <span className="font-medium">{opt.display_name}</span>
                                              <span className="text-xs font-semibold text-muted-foreground">+${(opt.price || 0).toFixed(2)}</span>
                                            </div>
                                            {opt.description && (
                                              <span className="text-xs text-muted-foreground">{opt.description}</span>
                                            )}
                                          </div>
                                        </SelectItem>
                                      );
                                    })
                                  ) : (
                                    <SelectItem value="__none__" disabled>No options available</SelectItem>
                                  )}
                                </SelectContent>
                              </Select>
                            )}
                          </div>
                          <div className="w-24 shrink-0 text-right">
                            <Badge variant={selected && (!Array.isArray(selected) || selected.length > 0) ? "default" : "outline"} className={selected && (!Array.isArray(selected) || selected.length > 0) ? "bg-primary" : "text-muted-foreground"}>
                              Cost: ${
                                Array.isArray(selected)
                                  ? selected.reduce((sum, val) => sum + ((opts as any[]).find((o: any) => o.id === val)?.price || 0), 0).toFixed(2)
                                  : (selected ? ((opts as any[]).find((o: any) => o.id === selected)?.price || 0).toFixed(2) : "0.00")
                              }
                            </Badge>
                          </div>
                        </div>
                      )}

                      {isNumeric && stopsError && (
                        <div className="flex items-center gap-1.5 text-sm text-destructive">
                          <AlertCircle className="w-4 h-4" />
                          {stopsError}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
                </div>
              ))
            )}
          </CardContent>
          <CardFooter className="flex flex-col sm:flex-row items-center justify-between gap-4 border-t pt-6 bg-muted/10">
            <div className="flex flex-col">
              <p className="text-sm text-muted-foreground font-medium">
                {completedFeatures.length < activeFeatures.length
                  ? `${activeFeatures.length - completedFeatures.length} feature(s) remaining`
                  : "All features selected ✓"}
              </p>
              <p className="font-bold text-lg text-primary">
                Total Component Cost: ${totalCost.toFixed(2)}
              </p>
            </div>
            <Button
              size="lg"
              onClick={handleSaveAll}
              disabled={updateMutation.isPending || !isDirty || completedFeatures.length !== activeFeatures.length || !!stopsError}
              className="w-full sm:w-auto font-semibold"
            >
              {updateMutation.isPending ? (
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              ) : (
                <Save className="w-5 h-5 mr-2" />
              )}
              Save Configuration
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Unsaved Changes Dialog */}
      <Dialog open={blocker.state === "blocked"} onOpenChange={(open) => { if (!open) blocker.reset?.(); }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-500" />
              Unsaved Changes
            </DialogTitle>
            <DialogDescription>
              You have unsaved changes in your elevator configuration. What would you like to do?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col sm:flex-row gap-2 sm:gap-0 sm:justify-end mt-4">
            <Button variant="outline" onClick={() => blocker.reset?.()}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={() => { localStorage.removeItem(draftKey); setIsDirty(false); blocker.proceed?.(); }}>
              Discard Changes
            </Button>
            <Button 
              onClick={() => handleSaveAll()} 
              disabled={updateMutation.isPending || !!stopsError}
            >
              {updateMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
