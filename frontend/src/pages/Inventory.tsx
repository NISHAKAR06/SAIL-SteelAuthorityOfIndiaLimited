import { motion } from "framer-motion";
import { Package, Warehouse, TrendingUp, AlertTriangle, Plus, Search, Loader2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useState, useEffect } from "react";
import api from "@/lib/api";

interface InventoryItem {
  id: string;
  material: string;
  grade: string;
  stockyard: string;
  quantity: number;
  unit: string;
  available: number;
  reserved: number;
  location: string;
  lastUpdated: string;
  quality: 'A' | 'B' | 'C';
  status: 'available' | 'low-stock' | 'critical' | 'reserved';
}

export default function Inventory() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStockyard, setSelectedStockyard] = useState("all");
  const [inventoryData, setInventoryData] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [plantsList, setPlantsList] = useState<string[]>([]);

  useEffect(() => {
    const fetchInventory = async () => {
      try {
        setLoading(true);
        console.log('Inventory: Starting to fetch inventory data...');

        const response = await api.staticData.getCurrentProductionInventory();
        console.log('Inventory: API Response received:', response);

        if (response.data) {
          console.log('Inventory: Raw data received:', response.data);
          console.log('Inventory: Sample inventory data:', response.data.slice(0, 2));

          // Transform the data to match our InventoryItem interface
          const transformedData: InventoryItem[] = response.data.map((item: any, index: number) => {
            console.log('Inventory: Processing inventory item:', item);

            // Map database fields to frontend fields
            // Handle quantity field variations from database
            const quantity = Number(item.quantity || item.inventory_tonnes || 0);
            const reservedPercent = Math.random() * 0.4; // Random reservation between 0-40%
            const reserved = Math.floor(quantity * reservedPercent);
            const available = quantity - reserved;

            // Determine status based on available quantity
            let status: 'available' | 'low-stock' | 'critical' | 'reserved' = 'available';
            if (available <= 0) {
              status = 'reserved';
            } else if (available < quantity * 0.15) {
              status = 'critical';
            } else if (available < quantity * 0.3) {
              status = 'low-stock';
            }

            // Extract plant name from location or use default
            let stockyard = item.plant_location || item.plant || 'Bokaro Plant';

            // Set quality grade based on material quality or random
            const qualities: Array<'A' | 'B' | 'C'> = ['A', 'B', 'C'];
            const quality = qualities[Math.floor(Math.random() * qualities.length)];

            // Ensure all required fields are present
            const inventoryItem = {
              id: `INV-${String(index + 1).padStart(6, '0')}`,
              material: item.product_name || item.material || 'Steel Product',
              grade: item.material_grade || item.grade || 'Standard',
              stockyard: stockyard,
              quantity: quantity,
              unit: item.unit || 'tons',
              available: available,
              reserved: reserved,
              location: item.storage_location || item.location || 'General Storage',
              lastUpdated: item.production_schedule_date ||
                         (new Date().toISOString().split('T')[0]),
              quality: quality,
              status: status
            };

            console.log('Inventory: Transformed item:', inventoryItem);
            return inventoryItem;
          });
          
          setInventoryData(transformedData);
          
          // Extract unique plant names for the dropdown
          const plants = Array.from(new Set(transformedData.map(item => item.stockyard)));
          setPlantsList(plants);
        }
        
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch inventory data:", err);
        setError("Failed to load inventory data. Please try again later.");
        setLoading(false);
        setInventoryData([]);
      }
    };
    
    fetchInventory();
  }, []);

  const filteredInventory = inventoryData.filter(item => {
    const matchesSearch = item.material.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.grade.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.stockyard.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStockyard = selectedStockyard === "all" || item.stockyard === selectedStockyard;
    return matchesSearch && matchesStockyard;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-green-500';
      case 'low-stock': return 'bg-yellow-500';
      case 'critical': return 'bg-red-500';
      case 'reserved': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'A': return 'text-green-600 bg-green-100';
      case 'B': return 'text-blue-600 bg-blue-100';
      case 'C': return 'text-orange-600 bg-orange-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in-up" style={{ position: 'relative', zIndex: 1 }}>
      {/* Loading State */}
      {loading && (
        <Card className="p-12 flex flex-col items-center justify-center bg-transparent backdrop-blur-sm border-border/50">
          <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
          <p className="text-lg text-muted-foreground">Loading inventory data...</p>
        </Card>
      )}
      
      {/* Error State section */}
      
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
      
      {/* Controls section */}
      
      {!loading && !error && (
        <div className="flex justify-end items-start">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Add Stock
          </Button>
        </div>
      )}
      
      {/* Summary Cards section */}
      
      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 auto-rows-fr">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="w-full p-6 bg-transparent backdrop-blur-sm border-border/50 h-32 flex flex-col justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-primary/10 rounded-xl">
                  <Package className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Materials</p>
                  <p className="text-2xl font-bold">{inventoryData.length}</p>
                </div>
              </div>
            </Card>
          </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="w-full p-6 bg-transparent backdrop-blur-sm border-border/50 h-32 flex flex-col justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-500/10 rounded-xl">
                <Warehouse className="h-6 w-6 text-green-500" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Available Stock</p>
                <p className="text-2xl font-bold">
                  {inventoryData.reduce((sum, item) => sum + item.available, 0).toLocaleString()} tons
                </p>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="w-full p-6 bg-transparent backdrop-blur-sm border-border/50 h-32 flex flex-col justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-500/10 rounded-xl">
                <TrendingUp className="h-6 w-6 text-blue-500" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Reserved Stock</p>
                <p className="text-2xl font-bold">
                  {inventoryData.reduce((sum, item) => sum + item.reserved, 0).toLocaleString()} tons
                </p>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="w-full p-6 bg-transparent backdrop-blur-sm border-border/50 h-32 flex flex-col justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-500/10 rounded-xl">
                <AlertTriangle className="h-6 w-6 text-red-500" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Critical Items</p>
                <p className="text-2xl font-bold">
                  {inventoryData.filter(item => item.status === 'critical').length}
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
      )}

      {/* Filters and Search section will be below */}
      {!loading && !error && (
        <Card className="p-6 bg-transparent backdrop-blur-sm border-border/50">
          <div className="flex gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search materials, grades, or stockyards..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <select
              value={selectedStockyard}
              onChange={(e) => setSelectedStockyard(e.target.value)}
              className="px-3 py-2 border border-border rounded-lg bg-background"
            >
              <option value="all">All Plants</option>
              {plantsList.map(plant => (
                <option key={plant} value={plant}>{plant}</option>
              ))}
            </select>
          </div>

        {/* Inventory Table */}
        <div className="space-y-3">
          {filteredInventory.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="p-4 hover:shadow-lg transition-shadow border-l-4 border-l-primary/20 bg-transparent backdrop-blur-sm border-border/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(item.status)}`} />
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{item.material}</h3>
                        <Badge className={getQualityColor(item.quality)}>
                          Grade {item.quality}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {item.grade} • {item.stockyard} • {item.location}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="flex items-center gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Available</p>
                        <p className="font-semibold">{item.available.toLocaleString()} {item.unit}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Reserved</p>
                        <p className="font-semibold text-blue-600">{item.reserved.toLocaleString()} {item.unit}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Total</p>
                        <p className="font-semibold">{item.quantity.toLocaleString()} {item.unit}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
        </Card>
      )}
    </div>
  );
}
