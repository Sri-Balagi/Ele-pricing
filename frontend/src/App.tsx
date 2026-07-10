import React, { Suspense } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/sonner";
import { queryClient } from "@/lib/queryClient";
import { AppLayout } from "@/layouts/AppLayout";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { WizardSkeleton } from "@/components/Skeletons";

// Lazy loaded pages
const Dashboard = React.lazy(() => import("@/pages/Dashboard"));
const ConfigDatabase = React.lazy(() => import("@/pages/ConfigDatabase"));
const Wizard = React.lazy(() => import("@/pages/Wizard"));
const Validation = React.lazy(() => import("@/pages/Validation"));
const BOM = React.lazy(() => import("@/pages/BOM"));
const Pricing = React.lazy(() => import("@/pages/Pricing"));
const Quote = React.lazy(() => import("@/pages/Quote"));

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<WizardSkeleton />}>
            <Dashboard />
          </Suspense>
        ),
      },
      {
        path: "database",
        element: (
          <Suspense fallback={<WizardSkeleton />}>
            <ConfigDatabase />
          </Suspense>
        ),
      },
      {
        path: "wizard",
        element: (
          <Suspense fallback={<WizardSkeleton />}>
            <Wizard />
          </Suspense>
        ),
      },
      {
        path: "validation",
        element: (
          <Suspense fallback={<WizardSkeleton />}>
            <Validation />
          </Suspense>
        ),
      },
      {
        path: "bom",
        element: (
          <Suspense fallback={<WizardSkeleton />}>
            <BOM />
          </Suspense>
        ),
      },
      {
        path: "pricing",
        element: (
          <Suspense fallback={<WizardSkeleton />}>
            <Pricing />
          </Suspense>
        ),
      },
      {
        path: "quote",
        element: (
          <Suspense fallback={<WizardSkeleton />}>
            <Quote />
          </Suspense>
        ),
      },
    ],
  },
]);

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <RouterProvider router={router} />
      </ErrorBoundary>
      <Toaster position="top-right" richColors />
    </QueryClientProvider>
  );
}
