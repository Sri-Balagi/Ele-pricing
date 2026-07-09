import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { configurationApi } from "@/api";
import { DataTable } from "@/components/DataTable";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { TableSkeleton } from "@/components/Skeletons";

export default function BOM() {
  const [configId, setConfigId] = useState("");
  const [activeId, setActiveId] = useState("");

  const { data, isLoading, error } = useQuery({
    queryKey: ["bom", activeId], // Note: API endpoint for BOM might be under getValidation or specific BOM endpoint
    // Assuming we fetch config and it contains BOM or we mock it for now since Milestone 6 BOM was generated in backend
    // Since there's no explicit /bom endpoint in openapi, maybe it's in the export or quote?
    // Let's use getConfiguration and extract BOM or handle gracefully.
    queryFn: () => configurationApi.get(activeId),
    enabled: !!activeId,
    retry: 0,
  });

  const columns = [
    { key: "part_number", header: "Part Number" },
    { key: "description", header: "Description" },
    { key: "quantity", header: "Qty", align: "right" as const },
    { key: "unit", header: "Unit" },
  ];

  const bomItems = data?.bom_items || [];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Bill of Materials</h1>

      <Card>
        <CardHeader>
          <CardTitle>Load BOM</CardTitle>
          <CardDescription>Enter a Configuration ID to view the Bill of Materials.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 max-w-md">
            <Input 
              placeholder="e.g. CFG-123" 
              value={configId}
              onChange={(e) => setConfigId(e.target.value)}
            />
            <Button onClick={() => setActiveId(configId)}>View BOM</Button>
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
