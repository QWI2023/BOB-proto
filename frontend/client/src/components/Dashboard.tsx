import React, { useState } from 'react';
import { Plus, History } from 'lucide-react';
import { User, APIResponse } from '../types';
import Header from './Header';
import APIRequestForm from './APIRequestForm';
import ResponseCard from './ResponseCard';
import RequestHistory from './RequestHistory';
import APIService from '../services/api';

interface DashboardProps {
  user: User;
  onLogout: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState<'request' | 'history'>('request');
  const [loading, setLoading] = useState(false);
  const [latestResponse, setLatestResponse] = useState<APIResponse | null>(null);
  const [requestHistory, setRequestHistory] = useState(APIService.getRequestHistory());

  const handleAPIRequest = async (request: {
    type: string;
    amount?: number;
    vendorId?: string;
    geoLocation?: string;
  }) => {
    setLoading(true);
    try {
      const response = await APIService.sendAPIRequest(request);
      setLatestResponse(response);
      setRequestHistory(APIService.getRequestHistory());
    } catch (error) {
      console.error('API request failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} onLogout={onLogout} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <nav className="flex space-x-1 bg-white p-1 rounded-lg shadow-sm">
            <button
              onClick={() => setActiveTab('request')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-colors duration-200 ${
                activeTab === 'request'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <Plus className="w-4 h-4" />
              <span>New Request</span>
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-colors duration-200 ${
                activeTab === 'history'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <History className="w-4 h-4" />
              <span>History</span>
            </button>
          </nav>
        </div>

        {activeTab === 'request' ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <APIRequestForm onSubmit={handleAPIRequest} loading={loading} />
            </div>
            <div>
              {latestResponse ? (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Latest Response</h2>
                  <ResponseCard response={latestResponse} />
                </div>
              ) : (
                <div className="bg-white rounded-xl shadow-lg p-8 text-center">
                  <div className="text-gray-400 mb-4">
                    <Plus className="w-16 h-16 mx-auto" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Ready for your first request
                  </h3>
                  <p className="text-gray-500">
                    Fill out the form and click "Send Request" to see the response here.
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <RequestHistory requests={requestHistory} />
        )}
      </main>
    </div>
  );
};

export default Dashboard;