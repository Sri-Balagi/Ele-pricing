import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { configurationApi } from "@/api";
import { DataTable } from "@/components/DataTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { AlertTriangle } from "lucide-react";
import { TableSkeleton } from "@/components/Skeletons";
import { ConfigSearch } from "@/components/ConfigSearch";

export default function BOM() {
  const [configId, setConfigId] = useState("");
  const [activeId, setActiveId] = useState("");

  const { data, isLoading, error } = useQuery({
    queryKey: ["bom", activeId],
    queryFn: () => configurationApi.getBOM(activeId),
    enabled: !!activeId,
    retry: 0,
  });

  const columns = [
    { key: "component_id", header: "Component ID" },
    { key: "component_name", header: "Component Name" },
    { key: "reason", header: "Reason" },
    { key: "quantity", header: "Qty", align: "right" as const },
    { key: "unit_cost", header: "Unit Cost", align: "right" as const, cell: (item: any) => item.unit_cost !== null && item.unit_cost !== undefined ? `$${Number(item.unit_cost).toFixed(2)}` : 'N/A' }
  ];

  const bomItems = data?.items || [];
  
  const baseItems = bomItems.filter((item: any) => item.origin_type === "BASE");
  const featureItems = bomItems.filter((item: any) => item.origin_type !== "BASE");

  const baseTotal = baseItems.reduce((sum: number, item: any) => sum + (Number(item.unit_cost) || 0), 0);
  const featureTotal = featureItems.reduce((sum: number, item: any) => sum + (Number(item.unit_cost) || 0), 0);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Bill of Materials</h1>

      <Card className="overflow-visible">
        <CardHeader>
          <CardTitle>Load BOM</CardTitle>
          <CardDescription>Enter a Configuration ID to view the Bill of Materials.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 max-w-md">
            <ConfigSearch 
              onSelect={(id) => setConfigId(id)} 
              selectedId={configId} 
              placeholder="Search config to view BOM..." 
            />
            <Button onClick={() => setActiveId(configId)} disabled={!configId}>View BOM</Button>
          </div>
        </CardContent>
      </Card>

      {isLoading && <TableSkeleton rows={5} />}
      {error && (
        <div className="p-4 bg-destructive/10 text-destructive border border-destructive/20 rounded-md flex flex-col gap-2">
          <div className="flex items-center gap-2 font-semibold text-lg">
            <AlertTriangle className="w-5 h-5" />
            BOM Not Available
          </div>
          <p>Please ensure that 'Pricing' is implemented and validated first before generating the Bill of Materials for this configuration.</p>
        </div>
      )}

      {data && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Base Build Components</CardTitle>
              <CardDescription>Fundamental components covering the base elevator category and floor coverage.</CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable 
                data={baseItems} 
                columns={columns} 
                emptyTitle="No Base Components" 
                emptyDescription="No base components generated." 
              />
              <div className="flex justify-end pt-4 pr-4">
                <p className="font-bold text-lg">Base Build Total: ${baseTotal.toFixed(2)}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Feature Customization Components</CardTitle>
              <CardDescription>Additional components based on selected features and rules.</CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable 
                data={featureItems} 
                columns={columns} 
                emptyTitle="No Feature Components" 
                emptyDescription="No feature-specific components found." 
              />
              <div className="flex justify-end pt-4 pr-4">
                <p className="font-bold text-lg">Feature Components Total: ${featureTotal.toFixed(2)}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
