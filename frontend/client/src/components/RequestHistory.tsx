import React from 'react';
import { Clock, Filter, Search } from 'lucide-react';
import { APIRequest } from '../types';

interface RequestHistoryProps {
  requests: APIRequest[];
}

const RequestHistory: React.FC<RequestHistoryProps> = ({ requests }) => {
  const getStatusBadge = (status: string) => {
    const configs = {
      permit: 'bg-green-100 text-green-800',
      challenge: 'bg-yellow-100 text-yellow-800',
      deny: 'bg-red-100 text-red-800'
    };
    return configs[status as keyof typeof configs] || 'bg-gray-100 text-gray-800';
  };

  const formatAmount = (amount?: number) => {
    if (amount === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Request History</h2>
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search requests..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
            </div>
            <button className="flex items-center space-x-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors duration-200">
              <Filter className="w-4 h-4" />
              <span className="text-sm">Filter</span>
            </button>
          </div>
        </div>
      </div>

      <div className="p-6">
        {requests.length === 0 ? (
          <div className="text-center py-12">
            <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No requests yet. Make your first API request above.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {requests.map((request) => (
              <div
                key={request.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-gray-900 capitalize">
                      {request.type.replace('_', ' ')}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(request.status)}`}>
                      {request.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500">
                    {request.timestamp.toLocaleString()}
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Request ID:</span>
                    <div className="font-mono text-xs">{request.id}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Amount:</span>
                    <div className="font-medium">{formatAmount(request.amount)}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Vendor ID:</span>
                    <div className="font-medium">{request.vendorId || '-'}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Response Time:</span>
                    <div className="font-medium">{request.responseTime}ms</div>
                  </div>
                </div>

                {request.geoLocation && (
                  <div className="mt-2 text-sm">
                    <span className="text-gray-500">Location:</span>
                    <span className="ml-2 font-medium">{request.geoLocation}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RequestHistory;