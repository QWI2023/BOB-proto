import React from 'react';
import { 
  Activity, 
  Shield, 
  AlertTriangle, 
  Clock,
  TrendingUp,
  Database,
  Download,
  FileText,
  Users
} from 'lucide-react';
import { MetricCard } from './MetricCard';
import { Button } from '../ui/Button';
import { useAuth } from '../../contexts/AuthContext';

export const OverviewPage: React.FC = () => {
  const { user } = useAuth();

  const handleExportLogs = () => {
    // Mock export functionality
    const blob = new Blob(['Mock audit log data...'], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `qapi-audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total API Requests"
          value="147,329"
          subtitle="Today"
          icon={Activity}
          trend={{ value: 12, label: 'vs yesterday', positive: true }}
          color="blue"
        />
        <MetricCard
          title="Threats Blocked"
          value="1,247"
          subtitle="This week"
          icon={Shield}
          trend={{ value: 8, label: 'vs last week', positive: true }}
          color="green"
        />
        <MetricCard
          title="Active Anomalies"
          value="23"
          subtitle="Requires attention"
          icon={AlertTriangle}
          trend={{ value: -15, label: 'vs yesterday', positive: true }}
          color="orange"
        />
        <MetricCard
          title="Avg Response Time"
          value="284ms"
          subtitle="Last 24h"
          icon={Clock}
          trend={{ value: -5, label: 'improvement', positive: true }}
          color="purple"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Button className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-2 h-20 text-center">
            <Database className="h-6 w-6" />
            <div className="sm:text-left">
              <div className="font-medium">📊 Live Dashboard</div>
              <div className="text-xs sm:text-sm opacity-75">View real-time metrics</div>
            </div>
          </Button>
          
          <Button 
            variant="secondary" 
            onClick={handleExportLogs}
            className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-2 h-20 text-center"
          >
            <Download className="h-6 w-6" />
            <div className="sm:text-left">
              <div className="font-medium">📁 Export Audit Logs</div>
              <div className="text-xs sm:text-sm opacity-75">Download system logs</div>
            </div>
          </Button>

          {user?.role === 'admin' && (
            <Button 
              variant="ghost" 
              className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-2 h-20 border-2 border-dashed border-gray-300 hover:border-gray-400 text-center sm:col-span-2 lg:col-span-1"
            >
              <Users className="h-6 w-6" />
              <div className="sm:text-left">
                <div className="font-medium">🏢 Manage Vendors</div>
                <div className="text-xs sm:text-sm opacity-75">Admin only</div>
              </div>
            </Button>
          )}
        </div>
      </div>

      {/* System Health Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">API Gateway</span>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                <span className="text-sm font-medium text-green-600">Operational</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Threat Detection</span>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                <span className="text-sm font-medium text-green-600">Active</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Self-Healing</span>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                <span className="text-sm font-medium text-yellow-600">Monitoring</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm text-gray-900">High-risk vendor detected</p>
                <p className="text-xs text-gray-500">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm text-gray-900">Rate limit applied to API endpoint</p>
                <p className="text-xs text-gray-500">5 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm text-gray-900">System health check completed</p>
                <p className="text-xs text-gray-500">10 minutes ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};