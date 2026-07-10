import React, { useState, useEffect } from "react";
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

const NUMERIC_INPUT_FEATURES = new Set(["FEAT-A-STOPS", "FEAT-B-STOPS", "FEAT-C-STOPS", "FEAT-STOPS"]);

export default function Wizard() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const editConfigId = searchParams.get("edit");
  const isEditMode = !!editConfigId;

  const [activeConfigId, setActiveConfigId] = useState<string | null>(null);
  const [projectName, setProjectName] = useState("");
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
        selectedCategory,
        featureSelections,
        stopsError
      }));
    }
  }, [draftLoaded, isDirty, activeConfigId, projectName, selectedCategory, featureSelections, stopsError, draftKey]);

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

  const catalogueLoading = loadingCats || loadingFeatures || loadingOptions || loadingConfig;

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
    createMutation.mutate({
      project_name: projectName.trim(),
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
        [`FEAT-B-STOPS`]: "STOPS-4", // min stops for CAT-B is 4
        "FEAT-B-CAPACITY": "OPT-B-CAP-630",
        "FEAT-B-SPEED": "OPT-B-SPD-100",
        "FEAT-B-DOOR-TYPE": "OPT-B-DOOR-SO",
        "FEAT-B-CABIN-FINISH": "OPT-B-FIN-SS",
        "FEAT-B-DEST-CTRL": "OPT-B-DEST-CONV",
        "FEAT-B-ENERGY-MODE": "OPT-B-NRG-STD",
        "FEAT-B-GROUP-CTRL": "OPT-B-GRP-STD"
      });
    } else if (val === "CAT-C") {
      setFeatureSelections({
        [`FEAT-C-STOPS`]: "STOPS-8", // min stops for CAT-C is 8
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
    setFeatureSelections((prev) => ({ ...prev, [featureId]: optionId }));
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
    if (isNaN(num) || num < 2) {
      setStopsError("Minimum 2 stops required.");
      return;
    }
    if (maxStops !== null && num > maxStops) {
      setStopsError(`Maximum ${maxStops} stops for ${activeCategoryObj?.name}.`);
      return;
    }
    setFeatureSelections((prev) => ({ ...prev, [featureId]: `STOPS-${num}` }));
  };

  const handleSaveAll = () => {
    if (!activeConfigId) return;
    if (stopsError) { toast.error("Please fix the Number of Stops before saving."); return; }
    const selectedOptions = Object.values(featureSelections).flat().filter(Boolean) as string[];
    updateMutation.mutate({ 
      id: activeConfigId, 
      data: { 
        project_name: projectName.trim(),
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
          <div className="space-y-2">
            <Label htmlFor="project_name" className="font-semibold">Project Name <span className="text-destructive">*</span></Label>
            <Input
              id="project_name"
              placeholder="e.g. Skyline Towers Phase 1"
              value={projectName}
              onChange={(e) => { setProjectName(e.target.value); setIsDirty(true); }}
              disabled={!!activeConfigId && !isEditMode} // Lock unless editing
            />
          </div>
        </CardContent>
        {!activeConfigId && (
          <CardFooter>
            <Button onClick={handleStartProject} disabled={!projectName.trim() || createMutation.isPending} className="ml-auto">
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
              activeFeatures.map((feature, idx) => {
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
                    else if (selectedCategory === "CAT-B") numericCost = Math.max(0, numStops - 4) * 3800;
                    else if (selectedCategory === "CAT-C") numericCost = Math.max(0, numStops - 8) * 8500;
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
                                  <SelectValue placeholder={`— Choose ${feature.name} —`} />
                                </SelectTrigger>
                                <SelectContent>
                                  {opts.length > 0 ? (
                                    opts.map((opt: any) => (
                                      <SelectItem key={opt.id} value={opt.id}>
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
                                    ))
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
              })
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
