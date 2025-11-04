import React, { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Train,
  LayoutDashboard,
  ListOrdered,
  Sparkles,
  Play,
  Bell,
  BellOff,
  Package,
  MapPin,
  TrendingUp,
  BarChart3,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ThemeToggle } from "@/components/ThemeToggle";
import DatabaseSeeder from "@/components/DatabaseSeeder";
// Steel plant themed background with subtle styling - no harsh shadows
const steelPlantBg = `linear-gradient(135deg,
  hsl(var(--background)) 0%,
  hsl(var(--muted)/0.02) 25%,
  hsl(var(--background)) 50%,
  hsl(var(--muted)/0.02) 75%,
  hsl(var(--background)) 100%
)`;

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/" },
  { icon: Train, label: "Rake Allocation", path: "/allocation" },
  { icon: ListOrdered, label: "Order Management", path: "/orders" },
  { icon: Package, label: "Inventory Management", path: "/inventory" },
  { icon: MapPin, label: "Loading Points", path: "/loading-points" },
  { icon: Sparkles, label: "AI Recommendations", path: "/ai" },
  { icon: TrendingUp, label: "Production Planning", path: "/production" },
  { icon: Play, label: "Live Simulation", path: "/simulation" },
  { icon: BarChart3, label: "Cost Optimization", path: "/cost-optimization" },
];

export default function Layout() {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-background w-full flex">
      {/* Clean Background - No shadows */}
      <div className="fixed inset-0 pointer-events-none bg-background">
      </div>

      {/* Collapsible Sidebar */}
      <aside className={cn(
        "bg-background/95 backdrop-blur-sm border-r border-border/20 transition-all duration-300 flex flex-col shadow-sm flex-shrink-0",
        sidebarCollapsed ? "w-20" : "w-80"
      )}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-xl">
                <Train className="h-6 w-6 text-primary" />
              </div>
              {!sidebarCollapsed && (
                <span className="font-bold text-lg text-foreground">
                  SAIL
                </span>
              )}
            </div>
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent/10"
              title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {sidebarCollapsed ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 p-4">
          <div className="space-y-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;

              return (
                <Link key={item.path} to={item.path}>
                  <div className={cn(
                    "flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 cursor-pointer",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-primary/10 text-foreground hover:text-primary"
                  )}>
                    <Icon className="h-5 w-5 flex-shrink-0" />
                    {!sidebarCollapsed && (
                      <span className="font-medium text-sm">{item.label}</span>
                    )}
                  </div>
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Sidebar Footer - Clean */}
        <div className="p-4 border-t border-border">
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-screen" style={{ maxWidth: 'calc(100vw - 20rem)' }}>
        {/* Page Header - Matching Sidebar Header Style */}
        <header className="px-8 bg-background/95 backdrop-blur-sm border-b border-border flex items-center justify-between" style={{ height: '81px', width: sidebarCollapsed ? 'calc(100vw - 5rem)' : 'calc(100vw - 20rem)' }}>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-xl">
                {navItems.find(item => item.path === location.pathname)?.icon ?
                  React.createElement(navItems.find(item => item.path === location.pathname)?.icon || LayoutDashboard, {
                    className: "h-6 w-6 text-primary"
                  }) :
                  <LayoutDashboard className="h-6 w-6 text-primary" />
                }
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">
                  {navItems.find(item => item.path === location.pathname)?.label || 'Dashboard'}
                </h1>
              </div>
            </div>
          </div>

          {/* Top Right Controls */}
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Button
              variant="outline"
              size="icon"
              onClick={() => setNotificationsEnabled(!notificationsEnabled)}
              className="h-10 w-10 relative hover:bg-accent/10"
            >
              <Bell className="h-[1.2rem] w-[1.2rem]" />
              {notificationsEnabled && (
                <Badge className="absolute -top-1 -right-1 h-6 w-6 flex items-center justify-center p-0 bg-accent text-accent-foreground text-xs">
                  3
                </Badge>
              )}
            </Button>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 p-6 overflow-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
