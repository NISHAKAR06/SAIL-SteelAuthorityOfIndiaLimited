import { motion } from "framer-motion";
import {
  ListOrdered,
  Package,
  Clock,
  CheckCircle2,
  Download,
  Loader2,
  Plus,
  Edit,
  Trash2,
  X,
  Save,
} from "lucide-react";
import MetricCard from "@/components/MetricCard";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { useState, useEffect } from "react";
import api from "@/lib/api";

interface OrderFormData {
  customer_name: string;
  customer_id?: number;
  material: string;
  quantity: number;
  unit: string;
  status: string;
  priority: string;
  origin_plant: string;
  destination: string;
  rate_per_ton?: number;
  preferred_dispatch_date?: string;
  latest_delivery_date?: string;
}

export default function Orders() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [orders, setOrders] = useState<any[]>([]);
  const [orderStats, setOrderStats] = useState({
    pendingOrders: 0,
    inProgressOrders: 0,
    completedToday: 0,
    totalOrders: 0,
  });

  // CRUD state management
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingOrder, setEditingOrder] = useState<any>(null);
  const [formData, setFormData] = useState<OrderFormData>({
    customer_name: '',
    customer_id: undefined,
    material: '',
    quantity: 1000,
    unit: 'tons',
    status: 'pending',
    priority: 'normal',
    origin_plant: 'Plant A',
    destination: '',
    rate_per_ton: undefined,
    preferred_dispatch_date: '',
    latest_delivery_date: '',
  });
  const [formLoading, setFormLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState<string | null>(null);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        console.log('Orders: Starting to fetch order data...');

        // Fetch orders from database orders table
        const response = await api.orders.getAll();
        console.log('Orders: API Response received:', response);

        if (response.data) {
          const ordersData = response.data;
          console.log('Orders: Raw data received:', ordersData);
          console.log('Orders: Sample data:', ordersData.slice(0, 2));

          setOrders(ordersData);

          // Calculate statistics from the orders data
          const pending = ordersData.filter((order: any) =>
            order.status?.toLowerCase() === "pending"
          ).length;

          const inProgress = ordersData.filter((order: any) =>
            order.status?.toLowerCase() === "in_progress"
          ).length;

          const completed = ordersData.filter((order: any) =>
            order.status?.toLowerCase() === "completed"
          ).length;

          console.log('Orders: Stats calculated:', { pending, inProgress, completed, total: ordersData.length });

          setOrderStats({
            pendingOrders: pending,
            inProgressOrders: inProgress,
            completedToday: completed, // For now, just show completed count
            totalOrders: ordersData.length,
          });
        }

        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch orders data:", err);
        setError("Failed to load orders data. Please try again later.");
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  // CRUD Handlers
  const resetForm = () => {
    setFormData({
      customer_name: '',
      customer_id: undefined,
      material: '',
      quantity: 1000,
      unit: 'tons',
      status: 'pending',
      priority: 'normal',
      origin_plant: 'Plant A',
      destination: '',
      rate_per_ton: undefined,
      preferred_dispatch_date: '',
      latest_delivery_date: '',
    });
  };

  const handleCreateOrder = async () => {
    try {
      setFormLoading(true);
      const response = await api.orders.create(formData);
      console.log('Order created:', response);

      // Refresh orders data
      const ordersResponse = await api.orders.getAll();
      if (ordersResponse.data) {
        setOrders(ordersResponse.data);
      }

      setIsCreateDialogOpen(false);
      resetForm();
    } catch (error) {
      console.error('Failed to create order:', error);
      alert('Failed to create order. Please try again.');
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditOrder = (order: any) => {
    setEditingOrder(order);
    setFormData({
      customer_name: order.customer_name || '',
      customer_id: order.customer_id,
      material: order.material || '',
      quantity: order.quantity || 1000,
      unit: order.unit || 'tons',
      status: order.status || 'pending',
      priority: order.priority || 'normal',
      origin_plant: order.origin_plant || 'Plant A',
      destination: order.destination || '',
      rate_per_ton: order.rate_per_ton,
      preferred_dispatch_date: order.preferred_dispatch_date || '',
      latest_delivery_date: order.latest_delivery_date || '',
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdateOrder = async () => {
    if (!editingOrder) return;

    try {
      setFormLoading(true);
      const response = await api.orders.update(editingOrder.id, formData);
      console.log('Order updated:', response);

      // Refresh orders data
      const ordersResponse = await api.orders.getAll();
      if (ordersResponse.data) {
        setOrders(ordersResponse.data);
      }

      setIsEditDialogOpen(false);
      setEditingOrder(null);
      resetForm();
    } catch (error) {
      console.error('Failed to update order:', error);
      alert('Failed to update order. Please try again.');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteOrder = async (orderId: string) => {
    try {
      setDeleteLoading(orderId);
      const response = await api.orders.delete(orderId);
      console.log('Order deleted:', response);

      // Remove from local state
      setOrders(prev => prev.filter(order => String(order.id) !== orderId));
    } catch (error) {
      console.error('Failed to delete order:', error);
      alert('Failed to delete order. Please try again.');
    } finally {
      setDeleteLoading(null);
    }
  };

  const handleDownload = () => {
    const ordersData = {
      summary: orderStats,
      orders: orders.slice(0, 10), // Include first 10 orders
      generatedAt: new Date().toISOString(),
      reportType: "Order Management",
    };

    const fileName = `orders_data_${
      new Date().toISOString().split("T")[0]
    }.json`;
    const blob = new Blob([JSON.stringify(ordersData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
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
          <p className="text-lg text-muted-foreground">
            Loading orders data...
          </p>
        </Card>
      )}

      <>{/* Error State */}</>

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
        <div className="flex justify-between items-start">
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Create Order
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create New Order</DialogTitle>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="customer_name">Customer Name</Label>
                  <Input
                    id="customer_name"
                    value={formData.customer_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, customer_name: e.target.value }))}
                    placeholder="Enter customer name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="customer_id">Customer ID</Label>
                  <Input
                    id="customer_id"
                    type="number"
                    value={formData.customer_id || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, customer_id: e.target.value ? parseInt(e.target.value) : undefined }))}
                    placeholder="Enter customer ID"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="material">Material</Label>
                  <Input
                    id="material"
                    value={formData.material}
                    onChange={(e) => setFormData(prev => ({ ...prev, material: e.target.value }))}
                    placeholder="Enter material type"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="quantity">Quantity</Label>
                  <Input
                    id="quantity"
                    type="number"
                    value={formData.quantity}
                    onChange={(e) => setFormData(prev => ({ ...prev, quantity: parseFloat(e.target.value) || 1000 }))}
                    placeholder="Enter quantity"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="unit">Unit</Label>
                  <Select value={formData.unit} onValueChange={(value) => setFormData(prev => ({ ...prev, unit: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select unit" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="tons">Tons</SelectItem>
                      <SelectItem value="kg">Kilograms</SelectItem>
                      <SelectItem value="pieces">Pieces</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select value={formData.status} onValueChange={(value) => setFormData(prev => ({ ...prev, status: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="in_progress">In Progress</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="priority">Priority</Label>
                  <Select value={formData.priority} onValueChange={(value) => setFormData(prev => ({ ...prev, priority: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="origin_plant">Origin Plant</Label>
                  <Select value={formData.origin_plant} onValueChange={(value) => setFormData(prev => ({ ...prev, origin_plant: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select plant" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Plant A">Plant A</SelectItem>
                      <SelectItem value="Plant B">Plant B</SelectItem>
                      <SelectItem value="Plant C">Plant C</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="destination">Destination</Label>
                  <Input
                    id="destination"
                    value={formData.destination}
                    onChange={(e) => setFormData(prev => ({ ...prev, destination: e.target.value }))}
                    placeholder="Enter destination"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="rate_per_ton">Rate per Ton</Label>
                  <Input
                    id="rate_per_ton"
                    type="number"
                    value={formData.rate_per_ton || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, rate_per_ton: e.target.value ? parseFloat(e.target.value) : undefined }))}
                    placeholder="Enter rate"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="preferred_dispatch_date">Preferred Dispatch Date</Label>
                  <Input
                    id="preferred_dispatch_date"
                    type="date"
                    value={formData.preferred_dispatch_date}
                    onChange={(e) => setFormData(prev => ({ ...prev, preferred_dispatch_date: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="latest_delivery_date">Latest Delivery Date</Label>
                  <Input
                    id="latest_delivery_date"
                    type="date"
                    value={formData.latest_delivery_date}
                    onChange={(e) => setFormData(prev => ({ ...prev, latest_delivery_date: e.target.value }))}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateOrder} disabled={formLoading}>
                  {formLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="h-4 w-4 mr-2" />}
                  Create Order
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          {/* Edit Order Dialog */}
          <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Edit Order</DialogTitle>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="edit_customer_name">Customer Name</Label>
                  <Input
                    id="edit_customer_name"
                    value={formData.customer_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, customer_name: e.target.value }))}
                    placeholder="Enter customer name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_customer_id">Customer ID</Label>
                  <Input
                    id="edit_customer_id"
                    type="number"
                    value={formData.customer_id || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, customer_id: e.target.value ? parseInt(e.target.value) : undefined }))}
                    placeholder="Enter customer ID"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_material">Material</Label>
                  <Input
                    id="edit_material"
                    value={formData.material}
                    onChange={(e) => setFormData(prev => ({ ...prev, material: e.target.value }))}
                    placeholder="Enter material type"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_quantity">Quantity</Label>
                  <Input
                    id="edit_quantity"
                    type="number"
                    value={formData.quantity}
                    onChange={(e) => setFormData(prev => ({ ...prev, quantity: parseFloat(e.target.value) || 1000 }))}
                    placeholder="Enter quantity"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_unit">Unit</Label>
                  <Select value={formData.unit} onValueChange={(value) => setFormData(prev => ({ ...prev, unit: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select unit" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="tons">Tons</SelectItem>
                      <SelectItem value="kg">Kilograms</SelectItem>
                      <SelectItem value="pieces">Pieces</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_status">Status</Label>
                  <Select value={formData.status} onValueChange={(value) => setFormData(prev => ({ ...prev, status: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="in_progress">In Progress</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_priority">Priority</Label>
                  <Select value={formData.priority} onValueChange={(value) => setFormData(prev => ({ ...prev, priority: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_origin_plant">Origin Plant</Label>
                  <Select value={formData.origin_plant} onValueChange={(value) => setFormData(prev => ({ ...prev, origin_plant: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select plant" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Plant A">Plant A</SelectItem>
                      <SelectItem value="Plant B">Plant B</SelectItem>
                      <SelectItem value="Plant C">Plant C</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_destination">Destination</Label>
                  <Input
                    id="edit_destination"
                    value={formData.destination}
                    onChange={(e) => setFormData(prev => ({ ...prev, destination: e.target.value }))}
                    placeholder="Enter destination"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_rate_per_ton">Rate per Ton</Label>
                  <Input
                    id="edit_rate_per_ton"
                    type="number"
                    value={formData.rate_per_ton || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, rate_per_ton: e.target.value ? parseFloat(e.target.value) : undefined }))}
                    placeholder="Enter rate"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_preferred_dispatch_date">Preferred Dispatch Date</Label>
                  <Input
                    id="edit_preferred_dispatch_date"
                    type="date"
                    value={formData.preferred_dispatch_date}
                    onChange={(e) => setFormData(prev => ({ ...prev, preferred_dispatch_date: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit_latest_delivery_date">Latest Delivery Date</Label>
                  <Input
                    id="edit_latest_delivery_date"
                    type="date"
                    value={formData.latest_delivery_date}
                    onChange={(e) => setFormData(prev => ({ ...prev, latest_delivery_date: e.target.value }))}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleUpdateOrder} disabled={formLoading}>
                  {formLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="h-4 w-4 mr-2" />}
                  Update Order
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          <Button onClick={handleDownload} variant="outline" className="gap-2">
            <Download className="h-4 w-4" />
            Download Data
          </Button>
        </div>
      )}

      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <MetricCard
              title="Pending Orders"
              value={orderStats.pendingOrders}
              icon={Clock}
              trend="Awaiting allocation"
              color="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <MetricCard
              title="In Progress"
              value={orderStats.inProgressOrders}
              icon={Package}
              trend="Being loaded"
              color="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <MetricCard
              title="Completed Today"
              value={orderStats.completedToday}
              icon={CheckCircle2}
              trend="+12 from yesterday"
              color="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <MetricCard
              title="Total Orders"
              value={orderStats.totalOrders}
              icon={ListOrdered}
              trend="This week"
              color="accent"
            />
          </motion.div>
        </div>
      )}

      {!loading && !error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="p-6 bg-transparent backdrop-blur-sm border-border/50">
            <h3 className="text-lg font-semibold mb-4">Recent Orders</h3>
            {orders.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="py-2 px-3 text-left font-medium text-sm">
                        Order ID
                      </th>
                      <th className="py-2 px-3 text-left font-medium text-sm">
                        Customer
                      </th>
                      <th className="py-2 px-3 text-left font-medium text-sm">
                        Product
                      </th>
                      <th className="py-2 px-3 text-left font-medium text-sm">
                        Quantity
                      </th>
                      <th className="py-2 px-3 text-left font-medium text-sm">
                        Delivery Date
                      </th>
                      <th className="py-2 px-3 text-left font-medium text-sm">
                        Status
                      </th>
                      <th className="py-2 px-3 text-left font-medium text-sm">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.slice(0, 10).map((order, index) => {
                      // Determine order status randomly for demo purposes
                      const statuses = ["pending", "in_progress", "completed"];
                      const orderStatus =
                        order.status ||
                        statuses[Math.floor(Math.random() * statuses.length)];

                      const getStatusBadge = (status: string) => {
                        switch (status) {
                          case "pending":
                            return (
                              <Badge
                                variant="outline"
                                className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-500"
                              >
                                Pending
                              </Badge>
                            );
                          case "in_progress":
                            return (
                              <Badge
                                variant="outline"
                                className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-500"
                              >
                                In Progress
                              </Badge>
                            );
                          case "completed":
                            return (
                              <Badge
                                variant="outline"
                                className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-500"
                              >
                                Completed
                              </Badge>
                            );
                          default:
                            return <Badge variant="outline">Unknown</Badge>;
                        }
                      };

                      return (
                        <tr
                          key={order.id || `order-${index}`}
                          className="border-b border-border/50 hover:bg-background/50"
                        >
                          <td className="py-3 px-3">
                            {`ORD-${String(order.id).padStart(4, "0")}`}
                          </td>
                          <td className="py-3 px-3">
                            {order.customer_name || "Customer " + (index + 1)}
                          </td>
                          <td className="py-3 px-3">
                            {order.material || "Steel Product"}
                          </td>
                          <td className="py-3 px-3">
                            {order.quantity || 1000} {order.unit || "tons"}
                          </td>
                          <td className="py-3 px-3">
                            {order.latest_delivery_date || "N/A"}
                          </td>
                          <td className="py-3 px-3">
                            {getStatusBadge(order.status || "pending")}
                          </td>
                          <td className="py-3 px-3">
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleEditOrder(order)}
                                className="h-8 w-8 p-0"
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <AlertDialog>
                                <AlertDialogTrigger asChild>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                                    disabled={deleteLoading === String(order.id)}
                                  >
                                    {deleteLoading === String(order.id) ? (
                                      <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                      <Trash2 className="h-4 w-4" />
                                    )}
                                  </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                  <AlertDialogHeader>
                                    <AlertDialogTitle>Delete Order</AlertDialogTitle>
                                    <AlertDialogDescription>
                                      Are you sure you want to delete order "ORD-{String(order.id).padStart(4, "0")}"?
                                      This action cannot be undone.
                                    </AlertDialogDescription>
                                  </AlertDialogHeader>
                                  <AlertDialogFooter>
                                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                                    <AlertDialogAction
                                      onClick={() => handleDeleteOrder(String(order.id))}
                                      className="bg-red-600 hover:bg-red-700"
                                    >
                                      Delete
                                    </AlertDialogAction>
                                  </AlertDialogFooter>
                                </AlertDialogContent>
                              </AlertDialog>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                No orders found. Please check back later.
              </div>
            )}
          </Card>
        </motion.div>
      )}
    </div>
  );
}
