import React, { useState } from 'react';
import { 
  Wifi, 
  WifiOff, 
  Filter,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { Button } from '../ui/Button';

export const LiveDashboard: React.FC = () => {
  const { data: requests, connected } = useWebSocket();
  const [filter, setFilter] = useState<'all' | 'success' | 'blocked' | 'flagged'>('all');

  const filteredRequests = requests.filter(req => 
    filter === 'all' || req.status === filter
  );

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-red-600 bg-red-50';
    if (score >= 60) return 'text-orange-600 bg-orange-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'blocked': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'flagged': return <AlertCircle className="h-4 w-4 text-orange-500" />;
      default: return <CheckCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Live Dashboard</h1>
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
            connected ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}>
            {connected ? <Wifi className="h-4 w-4" /> : <WifiOff className="h-4 w-4" />}
            <span>{connected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <Button variant="ghost" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <div className="flex flex-wrap gap-2">
            {[
              { key: 'all', label: 'All Requests' },
              { key: 'success', label: 'Success' },
              { key: 'blocked', label: 'Blocked' },
              { key: 'flagged', label: 'Flagged' }
            ].map((f) => (
              <button
                key={f.key}
                onClick={() => setFilter(f.key as any)}
                className={`px-3 py-1 rounded-lg text-sm transition-colors whitespace-nowrap ${
                  filter === f.key
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
          <div className="sm:ml-auto text-sm text-gray-500">
            {filteredRequests.length} requests
          </div>
        </div>
      </div>

      {/* Real-time Requests Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Real-time API Requests</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Endpoint
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vendor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mitigation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Response Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredRequests.slice(0, 20).map((request, index) => (
                <tr 
                  key={request.id} 
                  className={`hover:bg-gray-50 transition-colors ${
                    index === 0 && connected ? 'bg-blue-50' : ''
                  }`}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(request.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(request.status)}
                      <span className={`text-xs px-2 py-1 rounded-full capitalize ${
                        request.status === 'success' ? 'bg-green-100 text-green-800' :
                        request.status === 'blocked' ? 'bg-red-100 text-red-800' :
                        'bg-orange-100 text-orange-800'
                      }`}>
                        {request.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                    {request.endpoint}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {request.vendor}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium px-2 py-1 rounded ${getRiskColor(request.riskScore)}`}>
                      {request.riskScore}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {request.mitigation}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {request.responseTime}ms
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Audit Logs Panel */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Audit Logs</h2>
        <div className="space-y-3 max-h-60 overflow-y-auto">
          {[
            { time: '14:32:15', action: 'API request blocked', details: 'High risk score detected from VendorA' },
            { time: '14:31:42', action: 'Rate limit applied', details: 'Endpoint /api/users exceeded threshold' },
            { time: '14:30:18', action: 'Anomaly detected', details: 'Unusual traffic pattern identified' },
            { time: '14:29:55', action: 'Self-healing triggered', details: 'Auto-mitigation for suspicious IP' },
            { time: '14:28:33', action: 'Vendor status updated', details: 'VendorC moved to under review' }
          ].map((log, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50">
              <div className="text-xs text-gray-500 font-mono w-16 flex-shrink-0">
                {log.time}
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-gray-900">{log.action}</div>
                <div className="text-xs text-gray-600 mt-1">{log.details}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};