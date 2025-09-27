import React, { useState } from 'react';
import { Send, Loader } from 'lucide-react';

interface APIRequestFormProps {
  onSubmit: (request: {
    type: string;
    amount?: number;
    vendorId?: string;
    geoLocation?: string;
  }) => Promise<void>;
  loading: boolean;
}

const APIRequestForm: React.FC<APIRequestFormProps> = ({ onSubmit, loading }) => {
  const [requestType, setRequestType] = useState('transaction');
  const [amount, setAmount] = useState('');
  const [vendorId, setVendorId] = useState('');
  const [geoLocation, setGeoLocation] = useState('');

  const requestTypes = [
    { value: 'transaction', label: 'Transaction' },
    { value: 'catalog', label: 'Catalog' },
    { value: 'logs', label: 'Logs' },
    { value: 'user_data', label: 'User Data' },
    { value: 'reporting', label: 'Reporting' },
    { value: 'analytics', label: 'Analytics' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const request: any = {
      type: requestType,
    };

    if (amount) request.amount = parseFloat(amount);
    if (vendorId) request.vendorId = vendorId;
    if (geoLocation) request.geoLocation = geoLocation;

    await onSubmit(request);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">New API Request</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="requestType" className="block text-sm font-medium text-gray-700 mb-2">
            Request Type
          </label>
          <select
            id="requestType"
            value={requestType}
            onChange={(e) => setRequestType(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
            disabled={loading}
          >
            {requestTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
              Amount (Optional)
            </label>
            <input
              type="number"
              id="amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              placeholder="Enter amount"
              disabled={loading}
              step="0.01"
            />
          </div>

          <div>
            <label htmlFor="vendorId" className="block text-sm font-medium text-gray-700 mb-2">
              Vendor ID (Optional)
            </label>
            <input
              type="text"
              id="vendorId"
              value={vendorId}
              onChange={(e) => setVendorId(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              placeholder="Enter vendor ID"
              disabled={loading}
            />
          </div>
        </div>

        <div>
          <label htmlFor="geoLocation" className="block text-sm font-medium text-gray-700 mb-2">
            Geo-location (Optional)
          </label>
          <input
            type="text"
            id="geoLocation"
            value={geoLocation}
            onChange={(e) => setGeoLocation(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
            placeholder="Enter geo-location"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>Send Request</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default APIRequestForm;