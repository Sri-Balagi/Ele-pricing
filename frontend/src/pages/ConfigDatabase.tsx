import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { configurationApi } from "@/api";
import { toast } from "sonner";
import { FileText, Edit2, Trash2, Search, ArrowRight, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function ConfigDatabase() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");

  const { data: resultsEnvelope, isLoading } = useQuery({
    queryKey: ["configurations", "search", searchTerm],
    queryFn: () => searchTerm.length > 0 
      ? configurationApi.search(searchTerm) 
      : configurationApi.list(50, 0),
  });

  const deleteMutation = useMutation({
    mutationFn: configurationApi.delete,
    onSuccess: () => {
      toast.success("Configuration deleted successfully");
      queryClient.invalidateQueries({ queryKey: ["configurations"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard_metrics"] });
    },
    onError: () => {
      toast.error("Failed to delete configuration");
    }
  });

  const results = Array.isArray(resultsEnvelope) ? resultsEnvelope : [];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "CONFIGURED": return <Badge variant="secondary" className="bg-blue-100 text-blue-800 border-blue-200">Configured</Badge>;
      case "VALIDATED": return <Badge variant="secondary" className="bg-purple-100 text-purple-800 border-purple-200">Validated</Badge>;
      case "PRICED": return <Badge variant="secondary" className="bg-amber-100 text-amber-800 border-amber-200">Priced</Badge>;
      case "QUOTED": return <Badge variant="secondary" className="bg-emerald-100 text-emerald-800 border-emerald-200">Quoted</Badge>;
      case "EXPORTED": return <Badge variant="secondary" className="bg-emerald-100 text-emerald-800 border-emerald-200">Exported</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  const handleEdit = (id: string) => {
    navigate(`/wizard?edit=${id}`);
  };

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this configuration?")) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-20">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Configuration Database</h1>
          <p className="text-muted-foreground mt-1">Manage and search all customer elevator configurations.</p>
        </div>
        <button
          onClick={() => navigate("/wizard")}
          className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors shadow-sm font-medium"
        >
          New Configuration
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      <div className="bg-card border rounded-lg shadow-sm overflow-hidden">
        <div className="p-4 border-b bg-muted/20">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search by project name, customer name, or ID..."
              className="w-full pl-9 pr-4 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary/50"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        
        {isLoading ? (
          <div className="p-12 flex justify-center text-muted-foreground">
            <Loader2 className="w-6 h-6 animate-spin" />
          </div>
        ) : results.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-gray-900">No configurations found</h3>
            <p className="text-muted-foreground">Try adjusting your search or create a new configuration.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted-foreground uppercase bg-muted/30">
                <tr>
                  <th className="px-6 py-3 font-medium">ID</th>
                  <th className="px-6 py-3 font-medium">Project Name</th>
                  <th className="px-6 py-3 font-medium">Customer Name</th>
                  <th className="px-6 py-3 font-medium">Category</th>
                  <th className="px-6 py-3 font-medium">Status</th>
                  <th className="px-6 py-3 font-medium">Quote Value</th>
                  <th className="px-6 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {results.map((item: any) => (
                  <tr key={item.configuration_id} className="bg-card hover:bg-muted/10 transition-colors">
                    <td className="px-6 py-4 font-mono text-xs text-muted-foreground">
                      {item.configuration_id}
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-900">
                      {item.project_name || "Unnamed Project"}
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {item.customer_name || <span className="text-muted-foreground/50">-</span>}
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {item.selected_category === "CAT-A" ? "Type A (Residential)" : 
                       item.selected_category === "CAT-B" ? "Type B (Commercial)" : 
                       item.selected_category === "CAT-C" ? "Type C (Special)" : 
                       item.selected_category === "CAT-D" ? "Type D (Custom)" : item.selected_category}
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(item.status)}
                    </td>
                    <td className="px-6 py-4">
                      {item.pricing_total ? `€${item.pricing_total.toLocaleString()}` : <span className="text-muted-foreground/50">-</span>}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end items-center gap-2">
                        <button 
                          onClick={() => handleEdit(item.configuration_id)}
                          className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                          title="Edit"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleDelete(item.configuration_id)}
                          className="p-1.5 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                          title="Delete"
                          disabled={deleteMutation.isPending}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
