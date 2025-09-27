import React, { useState } from 'react';
import { CheckCircle, AlertTriangle, XCircle, Clock, Shield, X } from 'lucide-react';
import { APIResponse } from '../types';

interface ResponseCardProps {
  response: APIResponse;
}

const ResponseCard: React.FC<ResponseCardProps> = ({ response }) => {
  const [showMFAModal, setShowMFAModal] = useState(false);
  const [mfaCode, setMfaCode] = useState('');

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'permit':
        return {
          icon: CheckCircle,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          title: 'Request Permitted',
          description: 'All security checks passed successfully'
        };
      case 'challenge':
        return {
          icon: AlertTriangle,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          title: 'Challenge Required',
          description: 'Additional verification needed'
        };
      case 'deny':
        return {
          icon: XCircle,
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          title: 'Request Denied',
          description: 'Access denied by security policy'
        };
      default:
        return {
          icon: Clock,
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          title: 'Processing',
          description: 'Request is being processed'
        };
    }
  };

  const config = getStatusConfig(response.status);
  const IconComponent = config.icon;

  const handleMFASubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would verify the MFA code
    setShowMFAModal(false);
    setMfaCode('');
  };

  return (
    <>
      <div className={`${config.bgColor} ${config.borderColor} border rounded-xl p-6 transition-all duration-300 hover:shadow-md`}>
        <div className="flex items-start space-x-4">
          <div className={`${config.color} p-2 rounded-lg bg-white`}>
            <IconComponent className="w-6 h-6" />
          </div>
          
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <h3 className={`font-semibold text-lg ${config.color}`}>
                {config.title}
              </h3>
              <span className="text-sm text-gray-500">
                {response.responseTime}ms
              </span>
            </div>
            
            <p className="text-gray-700 mb-3">{response.message}</p>
            
            <div className="flex items-center justify-between text-sm text-gray-500">
              <span>Request ID: {response.requestId}</span>
              <span>{response.timestamp.toLocaleTimeString()}</span>
            </div>

            {response.challengeRequired && (
              <button
                onClick={() => setShowMFAModal(true)}
                className="mt-4 bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center space-x-2"
              >
                <Shield className="w-4 h-4" />
                <span>Complete MFA Challenge</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* MFA Modal */}
      {showMFAModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Multi-Factor Authentication</h3>
              <button
                onClick={() => setShowMFAModal(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleMFASubmit} className="space-y-4">
              <div>
                <label htmlFor="mfaCode" className="block text-sm font-medium text-gray-700 mb-2">
                  Enter your 6-digit authentication code
                </label>
                <input
                  type="text"
                  id="mfaCode"
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="000000"
                  maxLength={6}
                />
              </div>
              
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowMFAModal(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 px-4 rounded-lg transition-colors duration-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors duration-200"
                >
                  Verify
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default ResponseCard;