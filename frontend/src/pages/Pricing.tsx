import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { configurationApi } from "@/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/Skeletons";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

export default function Pricing() {
  const [configId, setConfigId] = useState("");
  const [activeId, setActiveId] = useState("");
  const [showPostTax, setShowPostTax] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["pricing", activeId],
    queryFn: () => configurationApi.getPricing(activeId),
    enabled: !!activeId,
    retry: 0,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Pricing Breakdown</h1>

      <Card>
        <CardHeader>
          <CardTitle>Load Pricing</CardTitle>
          <CardDescription>Enter a Configuration ID to view detailed pricing.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 max-w-md">
            <Input 
              placeholder="e.g. CFG-123" 
              value={configId}
              onChange={(e) => setConfigId(e.target.value)}
            />
            <Button onClick={() => setActiveId(configId)}>View Pricing</Button>
          </div>
        </CardContent>
      </Card>

      {isLoading && <TableSkeleton rows={3} />}
      
      {error && <div className="p-4 bg-destructive/10 text-destructive rounded-md">Error loading pricing</div>}

      {data && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle>Total Price</CardTitle>
              <CardDescription>Breakdown of all components and options.</CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Switch 
                id="tax-toggle" 
                checked={showPostTax} 
                onCheckedChange={setShowPostTax} 
              />
              <Label htmlFor="tax-toggle">Show Post-Tax</Label>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold mb-6 text-primary">
              ${(showPostTax ? data.total_price_incl_tax : data.total_price_excl_tax).toFixed(2)}
            </div>
            
            <h4 className="font-semibold mb-3">Line Items</h4>
            <div className="space-y-3">
              {data.line_items?.map((item: any, i: number) => (
                <div key={i} className="flex justify-between items-center py-2 border-b last:border-0">
                  <div>
                    <span className="font-medium">{item.description || item.rule_id}</span>
                  </div>
                  <div className="text-right">
                    <span>${(showPostTax ? (item.amount * 1.2 /* Mock tax if not supplied */) : item.amount).toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
