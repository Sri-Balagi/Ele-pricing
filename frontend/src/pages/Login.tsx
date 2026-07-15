import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Settings2, LogIn } from "lucide-react";

export default function Login() {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (userId === "L&T" && password === "L&T") {
      localStorage.setItem("isAuthenticated", "true");
      toast.success("Login successful!");
      navigate("/");
    } else {
      toast.error("Invalid User ID or Password");
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center p-4">
      <div className="mb-8 flex flex-col items-center gap-2">
        <div className="bg-primary/10 p-3 rounded-full">
          <Settings2 className="w-8 h-8 text-primary" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight">Elevator Configurator</h1>
      </div>

      <Card className="w-full max-w-md shadow-lg border-muted/50">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl text-center">Welcome back</CardTitle>
          <CardDescription className="text-center">
            Enter your credentials to access the system
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleLogin}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="userId">User ID</Label>
              <Input
                id="userId"
                placeholder="Enter your User ID"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button type="submit" className="w-full h-11 text-base">
              <LogIn className="w-4 h-4 mr-2" /> Sign In
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
