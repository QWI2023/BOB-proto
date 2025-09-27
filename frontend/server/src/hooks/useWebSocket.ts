import { useEffect, useRef, useState } from 'react';
import { APIRequest } from '../types';

export const useWebSocket = () => {
  const [data, setData] = useState<APIRequest[]>([]);
  const [connected, setConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Mock WebSocket connection with simulated data
    const mockWebSocket = () => {
      setConnected(true);
      
      const generateMockRequest = (): APIRequest => {
        const vendors = ['VendorA', 'VendorB', 'VendorC', 'VendorD'];
        const endpoints = ['/api/users', '/api/orders', '/api/products', '/api/auth'];
        const mitigations = ['None', 'Rate Limited', 'IP Blocked', 'Quarantined'];
        
        return {
          id: Math.random().toString(36).substr(2, 9),
          timestamp: new Date().toISOString(),
          endpoint: endpoints[Math.floor(Math.random() * endpoints.length)],
          vendor: vendors[Math.floor(Math.random() * vendors.length)],
          riskScore: Math.floor(Math.random() * 100),
          mitigation: mitigations[Math.floor(Math.random() * mitigations.length)],
          responseTime: Math.floor(Math.random() * 1000) + 50,
          status: Math.random() > 0.8 ? 'blocked' : Math.random() > 0.9 ? 'flagged' : 'success'
        };
      };

      const interval = setInterval(() => {
        const newRequest = generateMockRequest();
        setData(prev => [newRequest, ...prev.slice(0, 99)]); // Keep last 100 requests
      }, 2000 + Math.random() * 3000); // Random interval between 2-5 seconds

      return () => {
        clearInterval(interval);
        setConnected(false);
      };
    };

    const cleanup = mockWebSocket();
    return cleanup;
  }, []);

  return { data, connected };
};