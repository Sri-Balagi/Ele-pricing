import React, { Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/sonner";
import { queryClient } from "@/lib/queryClient";
import { AppLayout } from "@/layouts/AppLayout";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { WizardSkeleton } from "@/components/Skeletons";

// Lazy loaded pages
const Dashboard = React.lazy(() => import("@/pages/Dashboard"));
const Wizard = React.lazy(() => import("@/pages/Wizard"));
const Validation = React.lazy(() => import("@/pages/Validation"));
const BOM = React.lazy(() => import("@/pages/BOM"));
const Pricing = React.lazy(() => import("@/pages/Pricing"));
const Quote = React.lazy(() => import("@/pages/Quote"));

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<AppLayout />}>
              <Route index element={
                <Suspense fallback={<WizardSkeleton />}>
                  <Dashboard />
                </Suspense>
              } />
              <Route path="wizard" element={
                <Suspense fallback={<WizardSkeleton />}>
                  <Wizard />
                </Suspense>
              } />
              <Route path="validation" element={
                <Suspense fallback={<WizardSkeleton />}>
                  <Validation />
                </Suspense>
              } />
              <Route path="bom" element={
                <Suspense fallback={<WizardSkeleton />}>
                  <BOM />
                </Suspense>
              } />
              <Route path="pricing" element={
                <Suspense fallback={<WizardSkeleton />}>
                  <Pricing />
                </Suspense>
              } />
              <Route path="quote" element={
                <Suspense fallback={<WizardSkeleton />}>
                  <Quote />
                </Suspense>
              } />
            </Route>
          </Routes>
        </ErrorBoundary>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </QueryClientProvider>
  );
}
