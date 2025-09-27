import React, { useState, useEffect } from 'react';
import { 
  Wrench, 
  Activity, 
  TrendingUp, 
  Clock,
  Shield,
  Zap,
  CheckCircle,
  AlertCircle,
  Maximize2,
  Minimize2,
  X
} from 'lucide-react';
import { HealingAction } from '../../types';
import { MetricCard } from './MetricCard';
import { Button } from '../ui/Button';

export const SelfHealing: React.FC = () => {
  const [healingActions, setHealingActions] = useState<HealingAction[]>([]);
  const [windowStates, setWindowStates] = useState<{
    [key: string]: { minimized: boolean; maximized: boolean; closed: boolean }
  }>({
    metrics: { minimized: false, maximized: false, closed: false },
    status: { minimized: false, maximized: false, closed: false },
    actions: { minimized: false, maximized: false, closed: false },
    config: { minimized: false, maximized: false, closed: false }
  });

  useEffect(() => {
    // Mock healing actions data
    const mockActions: HealingAction[] = [
      {
        id: '1',
        timestamp: new Date().toISOString(),
        type: 'rate_limit',
        target: '/api/orders endpoint',
        effectiveness: 96,
        status: 'active'
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 10 * 60000).toISOString(),
        type: 'block_ip',
        target: '192.168.1.100',
        effectiveness: 100,
        status: 'active'
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 25 * 60000).toISOString(),
        type: 'quarantine_vendor',
        target: 'VendorX',
        effectiveness: 89,
        status: 'resolved'
      },
      {
        id: '4',
        timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
        type: 'rate_limit',
        target: '/api/users endpoint',
        effectiveness: 94,
        status: 'resolved'
      },
      {
        id: '5',
        timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
        type: 'block_ip',
        target: '10.0.0.50',
        effectiveness: 100,
        status: 'resolved'
      }
    ];
    setHealingActions(mockActions);
  }, []);

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'rate_limit': return <Clock className="h-4 w-4" />;
      case 'block_ip': return <Shield className="h-4 w-4" />;
      case 'quarantine_vendor': return <AlertCircle className="h-4 w-4" />;
      default: return <Wrench className="h-4 w-4" />;
    }
  };

  const getActionColor = (type: string) => {
    switch (type) {
      case 'rate_limit': return 'bg-blue-50 text-blue-600 border-blue-200';
      case 'block_ip': return 'bg-red-50 text-red-600 border-red-200';
      case 'quarantine_vendor': return 'bg-orange-50 text-orange-600 border-orange-200';
      default: return 'bg-gray-50 text-gray-600 border-gray-200';
    }
  };

  const getActionLabel = (type: string) => {
    switch (type) {
      case 'rate_limit': return 'Rate Limiting';
      case 'block_ip': return 'IP Blocking';
      case 'quarantine_vendor': return 'Vendor Quarantine';
      default: return type;
    }
  };

  const activeActions = healingActions.filter(action => action.status === 'active');
  const averageEffectiveness = healingActions.length > 0 
    ? Math.round(healingActions.reduce((sum, action) => sum + action.effectiveness, 0) / healingActions.length)
    : 0;

  const toggleWindow = (windowId: string, action: 'minimize' | 'maximize' | 'close') => {
    setWindowStates(prev => ({
      ...prev,
      [windowId]: {
        ...prev[windowId],
        minimized: action === 'minimize' ? !prev[windowId].minimized : false,
        maximized: action === 'maximize' ? !prev[windowId].maximized : false,
        closed: action === 'close' ? !prev[windowId].closed : prev[windowId].closed
      }
    }));
  };

  const WindowControls: React.FC<{ windowId: string; title: string }> = ({ windowId, title }) => {
    const state = windowStates[windowId];
    return (
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <Shield className="h-5 w-5 mr-2 text-blue-600" />
          {title}
        </h2>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => toggleWindow(windowId, 'minimize')}
            className="p-1 rounded hover:bg-gray-100 transition-colors"
            title="Minimize"
          >
            <Minimize2 className="h-4 w-4 text-gray-500" />
          </button>
          <button
            onClick={() => toggleWindow(windowId, 'maximize')}
            className="p-1 rounded hover:bg-gray-100 transition-colors"
            title={state.maximized ? "Restore" : "Maximize"}
          >
            <Maximize2 className="h-4 w-4 text-gray-500" />
          </button>
          <button
            onClick={() => toggleWindow(windowId, 'close')}
            className="p-1 rounded hover:bg-gray-100 transition-colors"
            title="Close"
          >
            <X className="h-4 w-4 text-gray-500" />
          </button>
        </div>
      </div>
    );
  };
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Self-Healing System</h1>
        <div className="text-sm text-gray-500">
          Auto-mitigation enabled
        </div>
      </div>

      {/* Effectiveness Metrics */}
      {!windowStates.metrics.closed && (
        <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all duration-300 ${
          windowStates.metrics.maximized ? 'fixed inset-4 z-50' : ''
        }`}>
          <WindowControls windowId="metrics" title="Effectiveness Metrics" />
          {!windowStates.metrics.minimized && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Active Mitigations"
                value={activeActions.length}
                subtitle="Currently running"
                icon={Zap}
                color="blue"
              />
              <MetricCard
                title="Avg Effectiveness"
                value={`${averageEffectiveness}%`}
                subtitle="Last 24 hours"
                icon={TrendingUp}
                trend={{ value: 5, label: 'vs yesterday', positive: true }}
                color="green"
              />
              <MetricCard
                title="Total Actions"
                value={healingActions.length}
                subtitle="Today"
                icon={Activity}
                color="purple"
              />
              <MetricCard
                title="Response Time"
                value="1.2s"
                subtitle="Avg detection to action"
                icon={Clock}
                trend={{ value: -12, label: 'improvement', positive: true }}
                color="orange"
              />
            </div>
          )}
        </div>
      )}

      {/* System Status */}
      {!windowStates.status.closed && (
        <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all duration-300 ${
          windowStates.status.maximized ? 'fixed inset-4 z-50' : ''
        }`}>
          <WindowControls windowId="status" title="System Status" />
          {!windowStates.status.minimized && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-medium text-gray-900">Threat Detection</h3>
                <p className="text-sm text-green-600 mt-1">Operational</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Zap className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-medium text-gray-900">Auto-Mitigation</h3>
                <p className="text-sm text-green-600 mt-1">Active</p>
              </div>
              <div className="text-center sm:col-span-2 lg:col-span-1">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Activity className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-medium text-gray-900">Monitoring</h3>
                <p className="text-sm text-blue-600 mt-1">24/7 Active</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recent Healing Actions */}
      {!windowStates.actions.closed && (
        <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden transition-all duration-300 ${
          windowStates.actions.maximized ? 'fixed inset-4 z-50' : ''
        }`}>
          <div className="px-6 py-4 border-b border-gray-200">
            <WindowControls windowId="actions" title="Recent Healing Actions" />
          </div>
          
          {!windowStates.actions.minimized && (
            <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
              {healingActions.map((action) => (
                <div key={action.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
                    <div className="flex items-center space-x-4">
                      <div className={`p-2 rounded-lg border-2 ${getActionColor(action.type)}`}>
                        {getActionIcon(action.type)}
                      </div>
                      <div>
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <h3 className="font-medium text-gray-900">{getActionLabel(action.type)}</h3>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            action.status === 'active' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {action.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">Target: {action.target}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(action.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-center sm:text-right">
                      <div className="text-lg font-semibold text-gray-900">
                        {action.effectiveness}%
                      </div>
                      <div className="text-sm text-gray-500">Effectiveness</div>
                      {action.status === 'active' && (
                        <Button size="sm" variant="ghost" className="mt-2">
                          Stop Action
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Configuration Panel */}
      {!windowStates.config.closed && (
        <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all duration-300 ${
          windowStates.config.maximized ? 'fixed inset-4 z-50' : ''
        }`}>
          <WindowControls windowId="config" title="Auto-Mitigation Rules" />
          {!windowStates.config.minimized && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 rounded-lg space-y-2 sm:space-y-0">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">Rate Limiting</h3>
                  <p className="text-sm text-gray-600">Auto-apply rate limits when request threshold exceeded</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-green-600">Enabled</span>
                  <div className="w-10 h-6 bg-green-500 rounded-full relative cursor-pointer">
                    <div className="w-4 h-4 bg-white rounded-full absolute top-1 right-1 transition-transform"></div>
                  </div>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 rounded-lg space-y-2 sm:space-y-0">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">IP Blocking</h3>
                  <p className="text-sm text-gray-600">Block suspicious IP addresses automatically</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-green-600">Enabled</span>
                  <div className="w-10 h-6 bg-green-500 rounded-full relative cursor-pointer">
                    <div className="w-4 h-4 bg-white rounded-full absolute top-1 right-1 transition-transform"></div>
                  </div>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 rounded-lg space-y-2 sm:space-y-0">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">Vendor Quarantine</h3>
                  <p className="text-sm text-gray-600">Isolate vendors with high risk scores</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Disabled</span>
                  <div className="w-10 h-6 bg-gray-300 rounded-full relative cursor-pointer">
                    <div className="w-4 h-4 bg-white rounded-full absolute top-1 left-1 transition-transform"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};