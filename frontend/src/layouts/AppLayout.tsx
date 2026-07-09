import React from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { healthApi } from "@/api";
import { Activity, LayoutDashboard, Settings2, FileText, CheckCircle2, Box, XCircle, AlertTriangle } from "lucide-react";

function StatusBar() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["liveness"],
    queryFn: healthApi.getLiveness,
    refetchInterval: 30000,
  });

  let statusColor = "bg-gray-400";
  let statusText = "Checking...";
  let Icon = Activity;

  if (isError) {
    statusColor = "bg-destructive";
    statusText = "Unavailable";
    Icon = XCircle;
  } else if (data) {
    if (data.status === "healthy") {
      statusColor = "bg-green-500";
      statusText = "Healthy";
      Icon = CheckCircle2;
    } else {
      statusColor = "bg-amber-500";
      statusText = "Degraded";
      Icon = AlertTriangle;
    }
  }

  return (
    <div className="h-8 border-t bg-muted/30 px-4 flex items-center justify-between text-xs text-muted-foreground z-10">
      <div className="flex items-center gap-2">
        <Icon className={`w-3 h-3 text-white rounded-full ${statusColor} p-0.5`} />
        <span>System Status: <strong className="text-foreground">{statusText}</strong></span>
      </div>
      <div>v{data?.version || "1.0.0"} | {data?.environment || "production"}</div>
    </div>
  );
}

export function AppLayout() {
  const location = useLocation();

  const navItems = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Wizard", path: "/wizard", icon: Settings2 },
    { name: "Validation", path: "/validation", icon: CheckCircle2 },
    { name: "BOM", path: "/bom", icon: Box },
    { name: "Pricing", path: "/pricing", icon: Activity },
    { name: "Quote & Export", path: "/quote", icon: FileText },
  ];

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background">
      {/* TopNav */}
      <header className="h-14 border-b flex items-center px-6 bg-card shrink-0">
        <h1 className="font-semibold text-lg flex items-center gap-2">
          <Settings2 className="w-5 h-5 text-primary" />
          Elevator Configurator
        </h1>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 border-r bg-muted/20 flex flex-col">
          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path || (item.path !== "/" && location.pathname.startsWith(item.path));
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                    isActive 
                      ? "bg-primary text-primary-foreground font-medium shadow-sm" 
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  <item.icon className="w-4 h-4" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-8 relative">
          <Outlet />
        </main>
      </div>

      <StatusBar />
    </div>
  );
}
