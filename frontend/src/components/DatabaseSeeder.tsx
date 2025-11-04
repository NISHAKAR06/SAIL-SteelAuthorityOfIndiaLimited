import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import api from '@/lib/api';
import { Database, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface SeedResult {
  success: boolean;
  message?: string;
  data?: any;
}

export default function DatabaseSeeder() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SeedResult | null>(null);
  const [stats, setStats] = useState<any>(null);

  const handleSeedDatabase = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await api.database.seedDatabase();
      setResult({ success: true, message: 'Database seeded successfully!', data: response.data });
    } catch (error: any) {
      setResult({
        success: false,
        message: error.message || 'Failed to seed database'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGetStats = async () => {
    setLoading(true);

    try {
      const response = await api.database.getStats();
      setStats(response.data);
    } catch (error: any) {
      setResult({
        success: false,
        message: error.message || 'Failed to get database stats'
      });
    } finally {
      setLoading(false);
    }
  };

  // Show always for now - will hide in production
  // const shouldShowSeeder = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  // if (!shouldShowSeeder) {
  //   return null;
  // }

  return (
    <Card className="p-4 bg-gradient-to-r from-blue-50 to-green-50 dark:from-blue-950 dark:to-green-950 border-blue-200 dark:border-blue-800">
      <div className="flex items-center gap-3 mb-4">
        <Database className="h-6 w-6 text-blue-600" />
        <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100">
          Database Management (Development Only)
        </h3>
      </div>

      <div className="space-y-4">
        <p className="text-sm text-blue-700 dark:text-blue-300">
          Seed the database with sample data from CSV files. This creates realistic data for development and testing.
        </p>

        <div className="flex gap-2">
          <Button
            onClick={handleSeedDatabase}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            Seed Database
          </Button>

          <Button
            onClick={handleGetStats}
            variant="outline"
            disabled={loading}
            className="border-blue-300 hover:bg-blue-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            Get Stats
          </Button>
        </div>

        {result && (
          <div className={`p-3 rounded-md flex items-center gap-2 ${
            result.success
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            {result.success ? (
              <CheckCircle className="h-4 w-4" />
            ) : (
              <AlertCircle className="h-4 w-4" />
            )}
            <span>{result.message}</span>
          </div>
        )}

        {stats && (
          <div className="bg-white dark:bg-gray-900 rounded-md p-3 border">
            <h4 className="font-semibold mb-2 text-blue-900 dark:text-blue-100">Database Stats</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {Object.entries(stats).map(([key, value]: [string, any]) => (
                <div key={key}>
                  <span className="font-medium">{key}:</span> {value}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
