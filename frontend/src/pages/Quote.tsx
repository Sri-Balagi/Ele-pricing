import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { quoteApi, exportApi } from "@/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Download, FileText, FileSpreadsheet, FileJson } from "lucide-react";
import { toast } from "sonner";

export default function Quote() {
  const [configId, setConfigId] = useState("");
  const [activeId, setActiveId] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["quote", activeId],
    queryFn: () => quoteApi.getQuoteInfo(activeId),
    enabled: !!activeId,
    retry: 0,
  });

  const handleDownload = async (format: string) => {
    try {
      setIsDownloading(true);
      const url = exportApi.getExportUrl(activeId, format);
      // Create a temporary anchor to trigger native browser download stream
      const a = document.createElement('a');
      a.href = url;
      a.download = `export-${activeId}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      toast.success(`${format.toUpperCase()} Export started`);
    } catch (e: any) {
      toast.error(`Export failed: ${e.message}`);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Quote & Export</h1>

      <Card>
        <CardHeader>
          <CardTitle>Load Quote</CardTitle>
          <CardDescription>Enter a Configuration ID to view quote details and export documents.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 max-w-md">
            <Input 
              placeholder="e.g. CFG-123" 
              value={configId}
              onChange={(e) => setConfigId(e.target.value)}
            />
            <Button onClick={() => setActiveId(configId)}>View Quote</Button>
          </div>
        </CardContent>
      </Card>

      {isLoading && <div className="animate-pulse h-32 bg-muted rounded-md" />}
      {error && <div className="p-4 bg-destructive/10 text-destructive rounded-md">Error loading Quote</div>}

      {data && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Quote Metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Quote Number</div>
                  <div className="font-semibold">{data.quote_metadata?.quote_number || "N/A"}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Version</div>
                  <div className="font-semibold">{data.quote_metadata?.quote_version || "1.0"}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Valid Until</div>
                  <div className="font-semibold">{data.quote_metadata?.valid_until || "N/A"}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Total Price</div>
                  <div className="font-semibold text-primary">${data.total_price?.toFixed(2) || "0.00"}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Export Documents</CardTitle>
              <CardDescription>Download configuration in various formats.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button 
                variant="outline" 
                className="w-full justify-start gap-3" 
                disabled={isDownloading}
                onClick={() => handleDownload('json')}
              >
                <FileJson className="w-4 h-4 text-amber-500" />
                Export as JSON
              </Button>
              <Button 
                variant="outline" 
                className="w-full justify-start gap-3" 
                disabled={isDownloading}
                onClick={() => handleDownload('pdf')}
              >
                <FileText className="w-4 h-4 text-red-500" />
                Export as PDF
              </Button>
              <Button 
                variant="outline" 
                className="w-full justify-start gap-3" 
                disabled={isDownloading}
                onClick={() => handleDownload('excel')}
              >
                <FileSpreadsheet className="w-4 h-4 text-green-500" />
                Export as Excel
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
