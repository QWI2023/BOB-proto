import React, { useState } from 'react';
import { Navigation } from './layout/Navigation';
import { OverviewPage } from './dashboard/OverviewPage';
import { LiveDashboard } from './dashboard/LiveDashboard';
import { AnomalyDetection } from './dashboard/AnomalyDetection';
import { SelfHealing } from './dashboard/SelfHealing';
import { VendorManagement } from './dashboard/VendorManagement';
import { AuditLogs } from './dashboard/AuditLogs';

export const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'overview': return <OverviewPage />;
      case 'live': return <LiveDashboard />;
      case 'anomalies': return <AnomalyDetection />;
      case 'healing': return <SelfHealing />;
      case 'vendors': return <VendorManagement />;
      case 'audit': return <AuditLogs />;
      default: return <OverviewPage />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderActiveTab()}
      </main>
    </div>
  );
};