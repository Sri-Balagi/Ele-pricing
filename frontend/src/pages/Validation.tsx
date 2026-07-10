import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { configurationApi } from "@/api";
import { DataTable } from "@/components/DataTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { AlertCircle, CheckCircle2, Play } from "lucide-react";
import { ConfigSearch } from "@/components/ConfigSearch";
import { toast } from "sonner";

export default function Validation() {
  const [configId, setConfigId] = useState("");
  const [activeId, setActiveId] = useState("");
  const queryClient = useQueryClient();

  const validateMutation = useMutation({
    mutationFn: (id: string) => configurationApi.validate(id),
    onSuccess: () => {
      toast.success("Validation pipeline completed!");
      queryClient.invalidateQueries({ queryKey: ["validation", activeId] });
      refetch();
    },
    onError: (err: any) => {
      toast.error(`Validation failed: ${err.message}`);
    }
  });

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["validation", activeId],
    queryFn: () => configurationApi.getValidation(activeId),
    enabled: !!activeId,
    retry: 0,
  });

  const columns = [
    { key: "code", header: "Rule Code" },
    { key: "message", header: "Message" },
    { 
      key: "severity", 
      header: "Severity",
      cell: (item: any) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          item.severity === "ERROR" ? "bg-destructive/20 text-destructive" : "bg-amber-500/20 text-amber-600"
        }`}>
          {item.severity}
        </span>
      )
    },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Validation View</h1>
      
      <Card className="overflow-visible">
        <CardHeader>
          <CardTitle>Check Configuration Validity</CardTitle>
          <CardDescription>Enter a Configuration ID to visualize rule execution, dependencies, and conflicts.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 max-w-md">
            <ConfigSearch 
              onSelect={(id) => setConfigId(id)} 
              selectedId={configId} 
              placeholder="Search config to validate..." 
            />
            <Button 
              onClick={() => {
                setActiveId(configId);
              }} 
              disabled={!configId}
              variant="outline"
            >
              View Results
            </Button>
            <Button 
              onClick={() => {
                setActiveId(configId);
                validateMutation.mutate(configId);
              }} 
              disabled={!configId || validateMutation.isPending}
            >
              <Play className="w-4 h-4 mr-2" />
              {validateMutation.isPending ? "Validating..." : "Run Validation"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {isLoading && <div className="animate-pulse h-32 bg-muted rounded-md" />}
      
      {error && (
        <div className="p-4 bg-destructive/10 text-destructive rounded-md flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          Failed to fetch validation: {(error as Error).message}
        </div>
      )}

      {data && (
        <div className="space-y-6">
          <div className={`p-4 rounded-md border flex items-center gap-3 ${
            data.validation_results?.is_valid ? "bg-green-500/10 border-green-500/20 text-green-700" : 
            (data.status === "CONFIGURED" ? "bg-amber-500/10 border-amber-500/20 text-amber-700" : "bg-destructive/10 border-destructive/20 text-destructive")
          }`}>
            {data.validation_results?.is_valid ? <CheckCircle2 className="w-6 h-6" /> : <AlertCircle className="w-6 h-6" />}
            <div>
              <h3 className="font-semibold text-lg">
                {data.validation_results?.is_valid ? "Configuration is Valid" : 
                 (data.status === "CONFIGURED" ? "Configuration not validated yet" : "Configuration has Conflicts")}
              </h3>
              <p className="text-sm opacity-90">
                {data.status === "CONFIGURED" 
                  ? "Click 'Run Validation' to execute the pipeline."
                  : `${(data.validation_results?.errors?.length || 0) + (data.validation_results?.warnings?.length || 0)} violations found.`
                }
              </p>
            </div>
          </div>

          <DataTable 
            data={[...(data.validation_results?.errors || []), ...(data.validation_results?.warnings || [])]} 
            columns={columns} 
            emptyTitle="No Violations" 
            emptyDescription="All rules passed successfully." 
          />
        </div>
      )}
    </div>
  );
}
