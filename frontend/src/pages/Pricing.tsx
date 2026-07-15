import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { configurationApi } from "@/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/Skeletons";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { ConfigSearch } from "@/components/ConfigSearch";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

export default function Pricing() {
  const [configId, setConfigId] = useState("");
  const [activeId, setActiveId] = useState("");
  const [showLogistics, setShowLogistics] = useState(false);
  const [showPostTax, setShowPostTax] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["pricing", activeId],
    queryFn: () => configurationApi.getPricing(activeId),
    enabled: !!activeId,
    retry: 0,
  });

  const validateMutation = useMutation({
    mutationFn: (id: string) => configurationApi.validate(id),
    onSuccess: (res) => {
      const errors = res?.errors || [];
      const hasErrors = errors.length > 0;
      const status = res?.final_configuration_status;

      if (!hasErrors && status !== "INVALID") {
        setActiveId(configId);
      } else {
        const msg = hasErrors ? errors[0] : "Configuration has conflicts.";
        toast.error(`Validation failed: ${msg}`);
      }
    },
    onError: (err: any) => {
      toast.error(`Error running validation: ${err.message}`);
    }
  });

  const handleViewPricing = () => {
    if (!configId) return;
    setActiveId("");
    validateMutation.mutate(configId);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Pricing Breakdown</h1>

      <Card className="overflow-visible">
        <CardHeader>
          <CardTitle>Load Pricing</CardTitle>
          <CardDescription>Enter a Configuration ID to view detailed pricing.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 max-w-md">
            <ConfigSearch
              onSelect={(id) => setConfigId(id)}
              selectedId={configId}
              placeholder="Search config to view pricing..."
            />
            <Button onClick={handleViewPricing} disabled={!configId || validateMutation.isPending}>
              {validateMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              View Pricing
            </Button>
          </div>
        </CardContent>
      </Card>

      {isLoading && <TableSkeleton rows={3} />}

      {error && <div className="p-4 bg-destructive/10 text-destructive rounded-md">Error loading pricing</div>}

      {data && (
        <Card>
          <CardHeader className="flex flex-row items-start justify-between pb-2">
            <div>
              <CardTitle>Total Price</CardTitle>
              <CardDescription>Breakdown of all components and options.</CardDescription>
            </div>
            <div className="flex flex-col items-end space-y-3">
              <div className="flex items-center space-x-2">
                <Switch
                  id="logistics-toggle"
                  checked={showLogistics}
                  onCheckedChange={(val) => {
                    setShowLogistics(val);
                    if (!val) setShowPostTax(false);
                  }}
                />
                <Label htmlFor="logistics-toggle">Show Post-Logistics</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="tax-toggle"
                  checked={showPostTax}
                  disabled={!showLogistics}
                  onCheckedChange={setShowPostTax}
                />
                <Label htmlFor="tax-toggle" className={!showLogistics ? "text-muted-foreground" : ""}>Show Post-Tax</Label>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold mb-6 text-primary">
              ${(Number(data.subtotal_before_tax) * (showLogistics ? 1.1 : 1) * (showPostTax ? 1.18 : 1)).toFixed(2)}
            </div>

            <h4 className="font-semibold mb-3">Line Items</h4>
            <div className="space-y-3">
              {[
                { description: "Base Category Cost", amount: data.category_cost },
                { description: "Additional Floor Coverage", amount: data.floor_coverage_cost, subtext: "Combined cost of hoist ropes, cables, guide rails, doors, wiring, and installation for extra floors." },
                { description: "Features Cost", amount: data.feature_cost }
              ].map((item, i) => (
                <div key={i} className="flex justify-between items-center py-2 border-b last:border-0">
                  <div>
                    <span className="font-medium">{item.description}</span>
                    {item.subtext && <p className="text-xs text-muted-foreground">{item.subtext}</p>}
                  </div>
                  <div className="text-right">
                    <span>${(Number(item.amount) * (showPostTax ? 1.18 : 1)).toFixed(2)}</span>
                  </div>
                </div>
              ))}
              {showLogistics && (
                <div className="flex justify-between items-center py-2 border-b last:border-0">
                  <div>
                    <span className="font-medium">Logistics Cost</span>
                    <span className="font-small">  (This is an estimate, actual cost may vary depending on the region)</span>
                  </div>
                  <div className="text-right">
                    <span>${(Number(data.subtotal_before_tax) * 0.1 * (showPostTax ? 1.18 : 1)).toFixed(2)}</span>

                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
