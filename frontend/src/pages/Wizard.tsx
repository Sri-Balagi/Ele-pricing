import React, { useState, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
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
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { CheckCircle2, Circle, Loader2, RefreshCw, AlertCircle } from "lucide-react";

// Features that have no catalogue options and must be free-form numeric inputs
const NUMERIC_INPUT_FEATURES = new Set(["FEAT-STOPS"]);

export default function Wizard() {
  const [activeConfigId, setActiveConfigId] = useState<string | null>(null);
  const [customerReference, setCustomerReference] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  // Map of feature_id → selected option_id (or raw string for numeric features)
  const [featureSelections, setFeatureSelections] = useState<Record<string, string>>({});
  const [stopsError, setStopsError] = useState<string | null>(null);

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

  const catalogueLoading = loadingCats || loadingFeatures || loadingOptions;

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
  const hasUnsaved = selectedCategory !== "" || Object.keys(featureSelections).length > 0;
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (hasUnsaved && !activeConfigId) { e.preventDefault(); e.returnValue = ""; }
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [hasUnsaved, activeConfigId]);

  // ── Mutations ────────────────────────────────────────────────────────────────
  const createMutation = useMutation({
    mutationFn: configurationApi.create,
    onSuccess: (data: any) => {
      toast.success("Configuration created! Now select your features below.");
      setActiveConfigId(data.configuration_id);
    },
    onError: (error: any) => toast.error(error.message || "Failed to create configuration"),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: { id: string; options: string[] }) =>
      configurationApi.update(payload.id, { selected_feature_options: payload.options }),
    onSuccess: () => toast.success("Configuration updated successfully!"),
    onError: (error: any) => toast.error(error.message || "Failed to update configuration"),
  });

  // ── Handlers ─────────────────────────────────────────────────────────────────
  const handleCreate = () => {
    if (!selectedCategory) { toast.error("Please select an elevator category first."); return; }
    createMutation.mutate({
      customer_reference: customerReference || undefined,
      selected_category: selectedCategory,
    });
  };

  const handleDropdownChange = (featureId: string, optionId: string) => {
    setFeatureSelections((prev) => ({ ...prev, [featureId]: optionId }));
  };

  const handleStopsChange = (value: string) => {
    setStopsError(null);
    const num = parseInt(value, 10);
    if (value === "") {
      setFeatureSelections((prev) => { const next = { ...prev }; delete next["FEAT-STOPS"]; return next; });
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
    setFeatureSelections((prev) => ({ ...prev, "FEAT-STOPS": `STOPS-${num}` }));
  };

  const handleSaveFeatures = () => {
    if (!activeConfigId) return;
    if (stopsError) { toast.error("Please fix the Number of Stops before saving."); return; }
    const selectedOptions = Object.values(featureSelections).filter(Boolean);
    updateMutation.mutate({ id: activeConfigId, options: selectedOptions });
  };

  const handleNewSession = () => {
    setActiveConfigId(null);
    setSelectedCategory("");
    setCustomerReference("");
    setFeatureSelections({});
    setStopsError(null);
  };

  const completedFeatures = (features as any[]).filter((f) => featureSelections[f.id]);
  const stopsRawValue = featureSelections["FEAT-STOPS"]
    ? featureSelections["FEAT-STOPS"].replace("STOPS-", "")
    : "";

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Configuration Wizard</h1>
          <p className="text-muted-foreground mt-1">
            {activeConfigId ? `Session: ${activeConfigId}` : "Configure your elevator step by step."}
          </p>
        </div>
        {activeConfigId && (
          <Button variant="outline" onClick={handleNewSession}>
            <RefreshCw className="w-4 h-4 mr-2" /> New Session
          </Button>
        )}
      </div>

      {/* ── Step 1: Category ── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {activeConfigId
              ? <CheckCircle2 className="w-5 h-5 text-green-500" />
              : <Circle className="w-5 h-5 text-muted-foreground" />}
            Step 1 — Elevator Type &amp; Reference
          </CardTitle>
          <CardDescription>Select the elevator type and optionally provide a project reference.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="customer_reference">Customer Reference (Optional)</Label>
            <Input
              id="customer_reference"
              placeholder="e.g. ACME-Corp-Tower-1"
              value={customerReference}
              onChange={(e) => setCustomerReference(e.target.value)}
              disabled={!!activeConfigId}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="category-select">Elevator Category *</Label>
            {catalogueLoading ? (
              <div className="flex items-center gap-2 text-muted-foreground text-sm h-10">
                <Loader2 className="w-4 h-4 animate-spin" /> Loading options…
              </div>
            ) : (
              <Select value={selectedCategory} onValueChange={setSelectedCategory} disabled={!!activeConfigId}>
                <SelectTrigger id="category-select">
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
              <p className="text-xs text-muted-foreground">
                {activeCategoryObj?.description}
              </p>
            )}
          </div>
        </CardContent>
        {!activeConfigId && (
          <CardFooter>
            <Button onClick={handleCreate} disabled={!selectedCategory || createMutation.isPending} className="ml-auto">
              {createMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Start Configuration →
            </Button>
          </CardFooter>
        )}
      </Card>

      {/* ── Step 2: Features ── */}
      {activeConfigId && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                {completedFeatures.length === (features as any[]).length && (features as any[]).length > 0
                  ? <CheckCircle2 className="w-5 h-5 text-green-500" />
                  : <Circle className="w-5 h-5 text-muted-foreground" />}
                Step 2 — Feature Configuration
              </CardTitle>
              <Badge variant="outline">
                {completedFeatures.length}/{(features as any[]).length} selected
              </Badge>
            </div>
            <CardDescription>
              Configure each feature below. These define your elevator's specifications.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            {catalogueLoading ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" /> Loading features…
              </div>
            ) : (
              (features as any[]).map((feature, idx) => {
                const isNumeric = NUMERIC_INPUT_FEATURES.has(feature.id);
                const opts = optionsByFeature[feature.id] || [];
                const selected = featureSelections[feature.id];
                const isComplete = !!selected && !stopsError;

                return (
                  <div key={feature.id}>
                    {idx > 0 && <Separator className="mb-5" />}
                    <div className="space-y-2">
                      {/* Row: label + check icon */}
                      <div className="flex items-center justify-between">
                        <Label htmlFor={`feature-${feature.id}`} className="text-sm font-semibold">
                          {feature.name}
                          {feature.required && <span className="ml-1 text-destructive">*</span>}
                        </Label>
                        {isComplete && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                      </div>
                      <p className="text-xs text-muted-foreground">{feature.description}</p>

                      {/* ── Numeric input for FEAT-STOPS ── */}
                      {isNumeric ? (
                        <div className="flex items-center gap-3">
                          <Input
                            id={`feature-${feature.id}`}
                            type="number"
                            min={2}
                            max={maxStops ?? undefined}
                            placeholder="Enter number of stops"
                            defaultValue={stopsRawValue}
                            onChange={(e) => handleStopsChange(e.target.value)}
                            className={stopsError ? "border-destructive focus-visible:ring-destructive" : ""}
                          />
                          {maxStops !== null && (
                            <span className="text-sm text-muted-foreground whitespace-nowrap">
                              Max. No.: <strong>{maxStops}</strong>
                            </span>
                          )}
                        </div>
                      ) : (
                        /* ── Dropdown for all other features ── */
                        <Select value={selected || ""} onValueChange={(val) => handleDropdownChange(feature.id, val)}>
                          <SelectTrigger id={`feature-${feature.id}`}>
                            <SelectValue placeholder={`— Choose ${feature.name} —`} />
                          </SelectTrigger>
                          <SelectContent>
                            {opts.length > 0 ? (
                              opts.map((opt: any) => (
                                <SelectItem key={opt.id} value={opt.id}>
                                  <div className="flex flex-col">
                                    <span className="font-medium">{opt.display_name}</span>
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

                      {/* Inline error for stops */}
                      {feature.id === "FEAT-STOPS" && stopsError && (
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
          <CardFooter className="flex items-center justify-between">
            <p className="text-xs text-muted-foreground">
              {completedFeatures.length < (features as any[]).length
                ? `${(features as any[]).length - completedFeatures.length} feature(s) remaining`
                : "All features selected ✓"}
            </p>
            <Button
              onClick={handleSaveFeatures}
              disabled={updateMutation.isPending || Object.keys(featureSelections).length === 0 || !!stopsError}
            >
              {updateMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Save Features
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  );
}
