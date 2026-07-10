import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { dashboardApi } from "@/api/dashboard";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { TableSkeleton } from "@/components/Skeletons";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { FileText, Clock, CheckCircle2, TrendingUp, ArrowRight } from "lucide-react";

export default function Dashboard() {
  const navigate = useNavigate();
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard_metrics"],
    queryFn: dashboardApi.getMetrics,
  });

  if (isLoading) return <TableSkeleton rows={4} />;
  if (error) return <div>Failed to load dashboard data</div>;

  const metrics = data;

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-20">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Overview of customer elevator configurations and quotes.</p>
        </div>
        <div className="flex gap-4">
          <button
            onClick={() => navigate("/database")}
            className="flex items-center gap-2 bg-secondary text-secondary-foreground px-4 py-2 rounded-md hover:bg-secondary/80 transition-colors shadow-sm font-medium"
          >
            <FileText className="w-4 h-4" />
            View Database
          </button>
          <button
            onClick={() => navigate("/wizard")}
            className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors shadow-sm font-medium"
          >
            New Configuration
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-t-4 border-t-blue-500 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-500" />
              Total Configurations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">{metrics?.total_configurations || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">All active & historic sessions</p>
          </CardContent>
        </Card>
        
        <Card className="border-t-4 border-t-amber-500 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-500" />
              Configurations On Hold
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">{metrics?.configurations_on_hold || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Draft, validated, or priced</p>
          </CardContent>
        </Card>
        
        <Card className="border-t-4 border-t-emerald-500 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              Completed Quotes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">{metrics?.completed_quotes || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Exported & final</p>
          </CardContent>
        </Card>

        <Card className="border-t-4 border-t-purple-500 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-purple-500" />
              Average Quote Value
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {metrics?.average_quote_value ? `€${metrics.average_quote_value.toLocaleString()}` : "€0"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Across completed quotes</p>
          </CardContent>
        </Card>
      </div>
      
      <Card className="mt-8 border shadow-sm">
        <CardHeader className="bg-muted/30 border-b">
          <CardTitle>Welcome to Elevator Configurator</CardTitle>
          <CardDescription>Manage the end-to-end quotation workflow.</CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <p className="text-muted-foreground leading-relaxed">
            The platform is running in <strong>Production Mode</strong>. All data is persisted to the local SQLite database. 
            You can create new configurations via the <strong>Wizard</strong> or manage existing ones in the <strong>Database</strong>.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
