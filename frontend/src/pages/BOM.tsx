import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { configurationApi } from "@/api";
import { DataTable } from "@/components/DataTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
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
    { key: "unit_cost", header: "Unit Cost", align: "right" as const, render: (val: any) => val !== null && val !== undefined ? `$${Number(val).toFixed(2)}` : 'N/A' }
  ];

  const bomItems = data?.items || [];

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
      {error && <div className="p-4 bg-destructive/10 text-destructive rounded-md">Error loading BOM</div>}

      {data && (
        <Card>
          <CardHeader>
            <CardTitle>BOM Items</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable 
              data={bomItems} 
              columns={columns} 
              emptyTitle="No BOM found" 
              emptyDescription="No bill of materials is available for this configuration." 
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
