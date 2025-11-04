import { motion } from "framer-motion";
import {
  Train,
  MapPin,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Package,
  UserCheck,
  Loader2,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import api from "@/lib/api";

interface RakeStatus {
  id: string;
  available: boolean;
  currentLocation?: string;
  destination?: string;
  returnTime?: string;
  estimatedReturn?: string;
  status: "available" | "in-transit" | "loading" | "unloading" | "maintenance";
  lastUpdated: string;
}

interface AllocationResult {
  allocatedRake: RakeStatus | null;
  allocationTime: string;
  estimatedLoadingTime: string;
  destination: string;
}

export default function RakeAllocation() {
  const [allocatedRakes, setAllocatedRakes] = useState<AllocationResult[]>([]);
  const [showAllocationResult, setShowAllocationResult] = useState(false);
  const [rakeData, setRakeData] = useState<RakeStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRakeData = async () => {
      try {
        setLoading(true);
        console.log('RakeAllocation: Starting to fetch rake data...');

        const response = await api.staticData.getCurrentRakeStatus();
        console.log('RakeAllocation: API Response received:', response);

        // Handle the actual backend response structure: {last_updated: '...', data: [...], source: 'database'}
        let rakeArray = [];
        if (response && response.data && Array.isArray(response.data)) {
          console.log('RakeAllocation: Direct data array structure');
          rakeArray = response.data;
        } else if (response && response.data && response.data.data && Array.isArray(response.data.data)) {
          console.log('RakeAllocation: Wrapped data structure');
          rakeArray = response.data.data;
        } else if (response && Array.isArray(response)) {
          console.log('RakeAllocation: Directly received array');
          rakeArray = response;
        } else {
          console.error('RakeAllocation: Unexpected response structure:', response);
          setRakeData([]);
          setLoading(false);
          return;
        }

        if (rakeArray.length > 0) {
          console.log('RakeAllocation: Processing', rakeArray.length, 'rake records');

          // Transform the data for frontend display
          const transformedData: RakeStatus[] = rakeArray.map(
            (item: any, index: number) => {
              console.log('RakeAllocation: Processing rake item:', index, item);

              // Map database fields - handle multiple possible names
              const rake_number = item.rake_number || item.rake_id || `RAKE_${String(index + 1).padStart(3, '0')}`;
              const status_text = (item.status || 'Available').toLowerCase();
              const isAvailable = status_text === "available" || status_text === "idle" || status_text === "none";

              // Status mapping from database to UI enum
              let mappedStatus: "available" | "in-transit" | "loading" | "unloading" | "maintenance";
              if (isAvailable) {
                mappedStatus = "available";
              } else if (status_text.includes("transit") || status_text.includes("moving") || status_text.includes("dispatched")) {
                mappedStatus = "in-transit";
              } else if (status_text.includes("load") || status_text.includes("loading")) {
                mappedStatus = "loading";
              } else if (status_text.includes("unload")) {
                mappedStatus = "unloading";
              } else if (status_text.includes("maintenance")) {
                mappedStatus = "maintenance";
              } else {
                mappedStatus = "available"; // Default fallback
              }

              return {
                id: rake_number,
                available: isAvailable,
                currentLocation: item.current_location || item.location || "Bokaro Plant",
                destination: isAvailable ? undefined : item.destination || item.final_destination,
                returnTime: item.expected_arrival_date || item.arrival_date
                  ? new Date(item.expected_arrival_date || item.arrival_date).toLocaleTimeString()
                  : undefined,
                estimatedReturn: isAvailable
                  ? undefined
                  : `Available for loading in ${Math.floor(2 + Math.random() * 8)} hours`,
                status: mappedStatus,
                lastUpdated: item.last_maintenance_date || item.last_updated ||
                           item.updated_at || new Date().toLocaleTimeString(),
              };
            }
          );

          console.log('RakeAllocation: Successfully transformed', transformedData.length, 'rake items');
          console.log('RakeAllocation: Sample transformed item:', transformedData[0]);
          setRakeData(transformedData);
        } else {
          console.warn('RakeAllocation: Empty rake data array');
          setRakeData([]);
        }

        setLoading(false);
      } catch (err) {
        console.error("RakeAllocation: Failed to fetch rake data:", err);
        setError("Failed to load rake status data. Please try again later.");
        setLoading(false);

        // Set empty data if API fails
        setRakeData([]);
      }
    };

    fetchRakeData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "available":
        return "bg-green-500";
      case "in-transit":
        return "bg-blue-500";
      case "loading":
        return "bg-yellow-500";
      case "unloading":
        return "bg-orange-500";
      case "maintenance":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "available":
        return <CheckCircle className="h-4 w-4" />;
      case "in-transit":
        return <Train className="h-4 w-4" />;
      case "loading":
        return <Package className="h-4 w-4" />;
      case "unloading":
        return <MapPin className="h-4 w-4" />;
      case "maintenance":
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "available":
        return "Available";
      case "in-transit":
        return "In Transit";
      case "loading":
        return "Loading";
      case "unloading":
        return "Unloading";
      case "maintenance":
        return "Maintenance";
      default:
        return "Unknown";
    }
  };

  // Mock destinations for allocation
  const mockDestinations = [
    "Visakhapatnam Port",
    "Paradip Port",
    "Haldia Port",
    "Mumbai Port",
    "Chennai Port",
    "Kolkata Port",
  ];

  const handleAllocateRake = () => {
    // Find available rakes
    const availableRakes = rakeData.filter((rake) => rake.available);

    if (availableRakes.length === 0) {
      alert("No rakes are currently available for allocation!");
      return;
    }

    // Randomly select an available rake
    const randomIndex = Math.floor(Math.random() * availableRakes.length);
    const selectedRake = availableRakes[randomIndex];

    // Generate mock allocation data
    const currentTime = new Date().toLocaleTimeString();
    const estimatedLoadingTime = new Date(
      Date.now() + 2 * 60 * 60 * 1000
    ).toLocaleTimeString(); // 2 hours from now
    const randomDestination =
      mockDestinations[Math.floor(Math.random() * mockDestinations.length)];

    const newAllocation: AllocationResult = {
      allocatedRake: selectedRake,
      allocationTime: currentTime,
      estimatedLoadingTime,
      destination: randomDestination,
    };

    // Add to allocation history
    setAllocatedRakes((prev) => [newAllocation, ...prev]);
    setShowAllocationResult(true);

    // Auto-hide the result after 5 seconds
    setTimeout(() => {
      setShowAllocationResult(false);
    }, 5000);

    console.log("Rake allocated:", newAllocation);
  };

  return (
    <div
      className="space-y-6 animate-fade-in-up"
      style={{ position: "relative", zIndex: 1 }}
    >
      {/* Loading State */}
      {loading && (
        <Card className="p-12 flex flex-col items-center justify-center bg-transparent backdrop-blur-sm border-border/50">
          <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
          <p className="text-lg text-muted-foreground">Loading rake data...</p>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="p-6 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <Button
            variant="outline"
            className="mt-4"
            onClick={() => window.location.reload()}
          >
            Try Again
          </Button>
        </Card>
      )}

      {!loading && !error && (
        <>
          {/* Header with Allocate Rake Button in right corner */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold">Rake Status Dashboard</h2>
              <p className="text-muted-foreground mt-1">
                Real-time status of all rakes and their availability
              </p>
            </div>

            <div className="flex items-center gap-4">
              <Badge variant="outline" className="text-sm">
                Last updated: {new Date().toLocaleTimeString()}
              </Badge>
              <Button
                className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-3 text-lg font-semibold shadow-lg"
                onClick={handleAllocateRake}
              >
                <UserCheck className="h-5 w-5 mr-2" />
                Allocate Rake
              </Button>
            </div>
          </div>
        </>
      )}

      {/* Allocation Result Notification */}
      {showAllocationResult && allocatedRakes.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="mb-6"
        >
          <Card className="p-6 bg-green-500/10 border-green-500/20 backdrop-blur-sm">
            <div className="flex items-center gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                  <UserCheck className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-green-700 mb-2">
                  Rake Successfully Allocated!
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Rake ID:</span>
                    <p className="font-semibold text-green-600">
                      {allocatedRakes[0].allocatedRake?.id}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">
                      Current Location:
                    </span>
                    <p className="font-semibold">
                      {allocatedRakes[0].allocatedRake?.currentLocation}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Destination:</span>
                    <p className="font-semibold text-blue-600">
                      {allocatedRakes[0].destination}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">
                      Est. Loading Time:
                    </span>
                    <p className="font-semibold text-orange-600">
                      {allocatedRakes[0].estimatedLoadingTime}
                    </p>
                  </div>
                </div>
                <div className="mt-3 text-xs text-muted-foreground">
                  Allocated at: {allocatedRakes[0].allocationTime}
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Allocation History */}
      {!loading && !error && allocatedRakes.length > 0 && (
        <Card className="mb-6 bg-transparent backdrop-blur-sm border-border/50">
          <div className="p-4 border-b border-border">
            <h3 className="text-lg font-semibold">Recent Allocations</h3>
            <p className="text-sm text-muted-foreground">
              History of manually allocated rakes
            </p>
          </div>
          <div className="p-4">
            <div className="space-y-3">
              {allocatedRakes.slice(0, 5).map((allocation, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-muted/30 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <Train className="h-4 w-4 text-primary" />
                    <div>
                      <p className="font-semibold">
                        {allocation.allocatedRake?.id}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {allocation.allocatedRake?.currentLocation} →{" "}
                        {allocation.destination}
                      </p>
                    </div>
                  </div>
                  <div className="text-right text-sm">
                    <p className="font-medium">{allocation.allocationTime}</p>
                    <p className="text-muted-foreground">
                      Est. {allocation.estimatedLoadingTime}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Rake Status Table */}
      {!loading && !error && (
        <Card className="bg-transparent backdrop-blur-sm border-border/50">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-4 font-semibold">Rake ID</th>
                  <th className="text-left p-4 font-semibold">Status</th>
                  <th className="text-left p-4 font-semibold">
                    Current Location
                  </th>
                  <th className="text-left p-4 font-semibold">Destination</th>
                  <th className="text-left p-4 font-semibold">Return Time</th>
                  <th className="text-left p-4 font-semibold">Availability</th>
                  <th className="text-left p-4 font-semibold">Last Updated</th>
                </tr>
              </thead>
              <tbody>
                {rakeData.map((rake, index) => (
                  <motion.tr
                    key={rake.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`border-b border-border/50 hover:bg-muted/30 transition-colors ${
                      rake.available ? "bg-green-500/5" : ""
                    }`}
                  >
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <Train className="h-4 w-4 text-primary" />
                        <span className="font-bold">{rake.id}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-2 h-2 rounded-full ${getStatusColor(
                            rake.status
                          )}`}
                        />
                        <span className="text-sm">
                          {getStatusText(rake.status)}
                        </span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">{rake.currentLocation}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      {rake.destination ? (
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4 text-blue-500" />
                          <span className="text-sm text-blue-600 font-medium">
                            {rake.destination}
                          </span>
                        </div>
                      ) : (
                        <span className="text-sm text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="p-4">
                      {rake.returnTime ? (
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-orange-500" />
                          <span className="text-sm text-orange-600 font-medium">
                            {rake.returnTime}
                          </span>
                        </div>
                      ) : (
                        <span className="text-sm text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="p-4">
                      {rake.available ? (
                        <Badge className="bg-green-500 hover:bg-green-600">
                          Available
                        </Badge>
                      ) : (
                        <Badge variant="outline">Busy</Badge>
                      )}
                    </td>
                    <td className="p-4">
                      <span className="text-xs text-muted-foreground">
                        {rake.lastUpdated}
                      </span>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Card View for Small Screens */}
          <div className="block md:hidden space-y-4 mt-6">
            {rakeData.map((rake, index) => (
              <motion.div
                key={rake.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card
                  className={`p-4 bg-transparent backdrop-blur-sm border-border/50 ${
                    rake.available ? "border-green-500/20 bg-green-500/5" : ""
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Train className="h-4 w-4 text-primary" />
                        <span className="font-bold">{rake.id}</span>
                      </div>
                      <div
                        className={`w-3 h-3 rounded-full ${getStatusColor(
                          rake.status
                        )}`}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-muted-foreground">Status:</span>
                        <div className="flex items-center gap-1 mt-1">
                          {getStatusIcon(rake.status)}
                          <span>{getStatusText(rake.status)}</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Location:</span>
                        <div className="flex items-center gap-1 mt-1">
                          <MapPin className="h-3 w-3" />
                          <span>{rake.currentLocation}</span>
                        </div>
                      </div>
                      {rake.destination && (
                        <div>
                          <span className="text-muted-foreground">
                            Destination:
                          </span>
                          <div className="flex items-center gap-1 mt-1">
                            <MapPin className="h-3 w-3 text-blue-500" />
                            <span className="text-blue-600">
                              {rake.destination}
                            </span>
                          </div>
                        </div>
                      )}
                      {rake.returnTime && (
                        <div>
                          <span className="text-muted-foreground">Return:</span>
                          <div className="flex items-center gap-1 mt-1">
                            <Clock className="h-3 w-3 text-orange-500" />
                            <span className="text-orange-600">
                              {rake.returnTime}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>

                    {rake.estimatedReturn && (
                      <div className="p-2 bg-muted/50 rounded-lg">
                        <p className="text-xs text-muted-foreground">
                          Status Update:
                        </p>
                        <p className="text-sm font-medium">
                          {rake.estimatedReturn}
                        </p>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-2 border-t border-border/50">
                      <span className="text-xs text-muted-foreground">
                        Updated: {rake.lastUpdated}
                      </span>
                      {rake.available ? (
                        <Badge className="bg-green-500 hover:bg-green-600 text-xs">
                          Ready for Loading
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-xs">
                          Currently Busy
                        </Badge>
                      )}
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-transparent backdrop-blur-sm border-border/50">
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">
              {rakeData.filter((r) => r.available).length}
            </p>
            <p className="text-sm text-muted-foreground">Available Rakes</p>
          </div>
        </Card>
        <Card className="p-4 bg-transparent backdrop-blur-sm border-border/50">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">
              {rakeData.filter((r) => r.status === "in-transit").length}
            </p>
            <p className="text-sm text-muted-foreground">In Transit</p>
          </div>
        </Card>
        <Card className="p-4 bg-transparent backdrop-blur-sm border-border/50">
          <div className="text-center">
            <p className="text-2xl font-bold text-yellow-600">
              {rakeData.filter((r) => r.status === "loading").length}
            </p>
            <p className="text-sm text-muted-foreground">Loading</p>
          </div>
        </Card>
        <Card className="p-4 bg-transparent backdrop-blur-sm border-border/50">
          <div className="text-center">
            <p className="text-2xl font-bold text-red-600">
              {rakeData.filter((r) => r.status === "maintenance").length}
            </p>
            <p className="text-sm text-muted-foreground">Maintenance</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
