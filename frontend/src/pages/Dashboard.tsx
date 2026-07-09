import React from "react";
import { useQuery } from "@tanstack/react-query";
import { systemApi } from "@/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TableSkeleton } from "@/components/Skeletons";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["systemPipeline"],
    queryFn: systemApi.getPipelineDiagnostics,
  });

  if (isLoading) return <TableSkeleton rows={4} />;
  if (error) return <div>Failed to load dashboard data</div>;

  const metrics = data?.runtime_metrics;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Uptime</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.uptime_seconds}s</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Requests Processed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.total_requests_processed}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Pipeline Executions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.pipeline_executions}</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
