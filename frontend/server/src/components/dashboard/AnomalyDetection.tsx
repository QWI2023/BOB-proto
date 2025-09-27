import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  TrendingUp, 
  Clock, 
  CheckCircle,
  XCircle,
  Eye,
  Settings
} from 'lucide-react';
import { Anomaly } from '../../types';
import { Button } from '../ui/Button';

export const AnomalyDetection: React.FC = () => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [filter, setFilter] = useState<'all' | 'unresolved' | 'resolved'>('unresolved');

  useEffect(() => {
    // Mock anomaly data
    const mockAnomalies: Anomaly[] = [
      {
        id: '1',
        timestamp: new Date().toISOString(),
        type: 'traffic_spike',
        severity: 'high',
        description: 'Unusual traffic spike detected on /api/orders endpoint (300% increase)',
        accuracy: 94,
        resolved: false
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
        type: 'suspicious_pattern',
        severity: 'medium',
        description: 'Repeated failed authentication attempts from VendorB',
        accuracy: 87,
        resolved: false
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
        type: 'unusual_endpoint',
        severity: 'low',
        description: 'New endpoint accessed: /api/internal/debug',
        accuracy: 76,
        resolved: true
      },
      {
        id: '4',
        timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
        type: 'traffic_spike',
        severity: 'high',
        description: 'Coordinated attack pattern detected across multiple endpoints',
        accuracy: 98,
        resolved: true
      }
    ];
    setAnomalies(mockAnomalies);
  }, []);

  const filteredAnomalies = anomalies.filter(anomaly => {
    if (filter === 'all') return true;
    if (filter === 'resolved') return anomaly.resolved;
    return !anomaly.resolved;
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'low': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'traffic_spike': return <TrendingUp className="h-4 w-4" />;
      case 'suspicious_pattern': return <AlertTriangle className="h-4 w-4" />;
      case 'unusual_endpoint': return <Eye className="h-4 w-4" />;
      default: return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const resolveAnomaly = (id: string) => {
    setAnomalies(prev => prev.map(anomaly => 
      anomaly.id === id ? { ...anomaly, resolved: true } : anomaly
    ));
  };

  const unresolvedCount = anomalies.filter(a => !a.resolved).length;
  const highSeverityCount = anomalies.filter(a => !a.resolved && a.severity === 'high').length;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Anomaly Detection</h1>
        <Button variant="ghost" size="sm">
          <Settings className="h-4 w-4 mr-2" />
          Configure Rules
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Anomalies</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{unresolvedCount}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-orange-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Severity</p>
              <p className="text-2xl font-bold text-red-600 mt-1">{highSeverityCount}</p>
            </div>
            <XCircle className="h-8 w-8 text-red-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Detection Accuracy</p>
              <p className="text-2xl font-bold text-green-600 mt-1">94%</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex flex-wrap gap-2">
          {[
            { key: 'unresolved', label: 'Unresolved', count: unresolvedCount },
            { key: 'all', label: 'All Anomalies', count: anomalies.length },
            { key: 'resolved', label: 'Resolved', count: anomalies.length - unresolvedCount }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setFilter(tab.key as any)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2 whitespace-nowrap ${
                filter === tab.key
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <span>{tab.label}</span>
              <span className="bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded-full">
                {tab.count}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Anomalies List */}
      <div className="space-y-4">
        {filteredAnomalies.map((anomaly) => (
          <div
            key={anomaly.id}
            className={`bg-white rounded-xl shadow-sm border-2 p-6 transition-all hover:shadow-md ${
              getSeverityColor(anomaly.severity)
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4 flex-1">
                <div className={`p-2 rounded-lg ${getSeverityColor(anomaly.severity)}`}>
                  {getTypeIcon(anomaly.type)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className={`text-xs px-2 py-1 rounded-full uppercase tracking-wider font-medium ${
                      getSeverityColor(anomaly.severity)
                    }`}>
                      {anomaly.severity}
                    </span>
                    <span className="text-sm text-gray-500 capitalize">
                      {anomaly.type.replace('_', ' ')}
                    </span>
                    <div className="flex items-center text-sm text-gray-500">
                      <Clock className="h-4 w-4 mr-1" />
                      {new Date(anomaly.timestamp).toLocaleString()}
                    </div>
                  </div>
                  <p className="text-gray-900 font-medium mb-2">{anomaly.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>Accuracy: {anomaly.accuracy}%</span>
                    {anomaly.resolved ? (
                      <div className="flex items-center text-green-600">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Resolved
                      </div>
                    ) : (
                      <div className="flex items-center text-orange-600">
                        <AlertTriangle className="h-4 w-4 mr-1" />
                        Active
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex space-x-2 ml-4">
                {!anomaly.resolved && (
                  <Button
                    size="sm"
                    onClick={() => resolveAnomaly(anomaly.id)}
                    className="whitespace-nowrap"
                  >
                    Mark Resolved
                  </Button>
                )}
                <Button variant="ghost" size="sm">
                  View Details
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredAnomalies.length === 0 && (
        <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-200">
          <CheckCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No anomalies found</h3>
          <p className="text-gray-500">
            {filter === 'unresolved' 
              ? "All anomalies have been resolved."
              : `No ${filter} anomalies to display.`}
          </p>
        </div>
      )}
    </div>
  );
};