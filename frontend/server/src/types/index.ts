export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'employee';
}

export interface APIRequest {
  id: string;
  timestamp: string;
  endpoint: string;
  vendor: string;
  riskScore: number;
  mitigation: string;
  responseTime: number;
  status: 'success' | 'blocked' | 'flagged';
}

export interface Anomaly {
  id: string;
  timestamp: string;
  type: 'traffic_spike' | 'unusual_endpoint' | 'suspicious_pattern';
  severity: 'low' | 'medium' | 'high';
  description: string;
  accuracy: number;
  resolved: boolean;
}

export interface HealingAction {
  id: string;
  timestamp: string;
  type: 'rate_limit' | 'block_ip' | 'quarantine_vendor';
  target: string;
  effectiveness: number;
  status: 'active' | 'resolved';
}

export interface Vendor {
  id: string;
  name: string;
  status: 'active' | 'suspended' | 'under_review';
  riskLevel: 'low' | 'medium' | 'high';
  lastActivity: string;
  requestCount: number;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  resource: string;
  details: string;
}