import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  Search, 
  Filter,
  Calendar,
  User,
  Activity
} from 'lucide-react';
import { AuditLog } from '../../types';
import { Button } from '../ui/Button';

export const AuditLogs: React.FC = () => {
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState<string>('all');
  const [dateRange, setDateRange] = useState<string>('today');

  useEffect(() => {
    // Mock audit logs data
    const mockLogs: AuditLog[] = [
      {
        id: '1',
        timestamp: new Date().toISOString(),
        user: 'admin@qapishield.com',
        action: 'BLOCK_API_REQUEST',
        resource: '/api/orders',
        details: 'High risk score detected from VendorB (Score: 95)'
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
        user: 'system',
        action: 'AUTO_RATE_LIMIT',
        resource: '/api/users',
        details: 'Rate limit applied: 100 req/min threshold exceeded'
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 10 * 60000).toISOString(),
        user: 'employee@qapishield.com',
        action: 'VIEW_DASHBOARD',
        resource: 'live_dashboard',
        details: 'Accessed live dashboard page'
      },
      {
        id: '4',
        timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
        user: 'system',
        action: 'ANOMALY_DETECTED',
        resource: 'traffic_analysis',
        details: 'Unusual traffic pattern detected on /api/products'
      },
      {
        id: '5',
        timestamp: new Date(Date.now() - 20 * 60000).toISOString(),
        user: 'admin@qapishield.com',
        action: 'UPDATE_VENDOR_STATUS',
        resource: 'VendorC',
        details: 'Changed status from active to under_review'
      },
      {
        id: '6',
        timestamp: new Date(Date.now() - 25 * 60000).toISOString(),
        user: 'system',
        action: 'SELF_HEALING_TRIGGERED',
        resource: 'IP_192.168.1.100',
        details: 'Blocked suspicious IP address automatically'
      },
      {
        id: '7',
        timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
        user: 'admin@qapishield.com',
        action: 'EXPORT_LOGS',
        resource: 'audit_logs',
        details: 'Downloaded audit logs CSV file'
      },
      {
        id: '8',
        timestamp: new Date(Date.now() - 35 * 60000).toISOString(),
        user: 'employee@qapishield.com',
        action: 'RESOLVE_ANOMALY',
        resource: 'anomaly_001',
        details: 'Marked traffic spike anomaly as resolved'
      },
      {
        id: '9',
        timestamp: new Date(Date.now() - 40 * 60000).toISOString(),
        user: 'system',
        action: 'VENDOR_QUARANTINE',
        resource: 'VendorX',
        details: 'Quarantined vendor due to suspicious activity'
      },
      {
        id: '10',
        timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
        user: 'admin@qapishield.com',
        action: 'LOGIN',
        resource: 'authentication',
        details: 'User logged in successfully'
      }
    ];
    setAuditLogs(mockLogs);
  }, []);

  const filteredLogs = auditLogs.filter(log => {
    const matchesSearch = 
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.resource.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.details.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesAction = actionFilter === 'all' || log.action === actionFilter;
    
    // Simple date filtering - in a real app, this would be more sophisticated
    let matchesDate = true;
    if (dateRange === 'today') {
      const today = new Date().toDateString();
      matchesDate = new Date(log.timestamp).toDateString() === today;
    }
    
    return matchesSearch && matchesAction && matchesDate;
  });

  const handleExportLogs = () => {
    const csvContent = [
      ['Timestamp', 'User', 'Action', 'Resource', 'Details'].join(','),
      ...filteredLogs.map(log => [
        new Date(log.timestamp).toISOString(),
        log.user,
        log.action,
        log.resource,
        `"${log.details}"`
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `qapi-audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getActionColor = (action: string) => {
    if (action.includes('BLOCK') || action.includes('QUARANTINE')) {
      return 'bg-red-50 text-red-700 border-red-200';
    }
    if (action.includes('LOGIN') || action.includes('VIEW')) {
      return 'bg-blue-50 text-blue-700 border-blue-200';
    }
    if (action.includes('UPDATE') || action.includes('RESOLVE')) {
      return 'bg-green-50 text-green-700 border-green-200';
    }
    if (action.includes('ANOMALY') || action.includes('DETECTED')) {
      return 'bg-orange-50 text-orange-700 border-orange-200';
    }
    return 'bg-gray-50 text-gray-700 border-gray-200';
  };

  const getUserIcon = (user: string) => {
    return user === 'system' ? (
      <Activity className="h-4 w-4 text-blue-500" />
    ) : (
      <User className="h-4 w-4 text-gray-500" />
    );
  };

  const uniqueActions = [...new Set(auditLogs.map(log => log.action))].sort();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Audit Logs</h1>
        <Button onClick={handleExportLogs}>
          <Download className="h-4 w-4 mr-2" />
          Export Logs
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Logs</p>
              <p className="text-2xl font-bold text-gray-900">{auditLogs.length}</p>
            </div>
            <FileText className="h-8 w-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">System Actions</p>
              <p className="text-2xl font-bold text-green-600">
                {auditLogs.filter(log => log.user === 'system').length}
              </p>
            </div>
            <Activity className="h-8 w-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">User Actions</p>
              <p className="text-2xl font-bold text-purple-600">
                {auditLogs.filter(log => log.user !== 'system').length}
              </p>
            </div>
            <User className="h-8 w-8 text-purple-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Security Events</p>
              <p className="text-2xl font-bold text-red-600">
                {auditLogs.filter(log => 
                  log.action.includes('BLOCK') || 
                  log.action.includes('QUARANTINE') || 
                  log.action.includes('ANOMALY')
                ).length}
              </p>
            </div>
            <Activity className="h-8 w-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full"
            >
              <option value="all">All Actions</option>
              {uniqueActions.map(action => (
                <option key={action} value={action}>{action}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4 text-gray-500" />
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full"
            >
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="all">All Time</option>
            </select>
          </div>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Audit Trail ({filteredLogs.length} entries)
          </h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Resource
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Details
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {getUserIcon(log.user)}
                      <span className="text-sm text-gray-900">{log.user}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-xs px-3 py-1 rounded-full border ${getActionColor(log.action)}`}>
                      {log.action}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                    {log.resource}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600 max-w-xs">
                    <div className="truncate" title={log.details}>
                      {log.details}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredLogs.length === 0 && (
        <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-200">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No logs found</h3>
          <p className="text-gray-500">
            Try adjusting your search or filter criteria.
          </p>
        </div>
      )}
    </div>
  );
};