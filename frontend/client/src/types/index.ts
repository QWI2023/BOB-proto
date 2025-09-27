export interface User {
  id: string;
  username: string;
  role: string;
  token: string;
}

export interface APIRequest {
  id: string;
  type: string;
  amount?: number;
  vendorId?: string;
  geoLocation?: string;
  timestamp: Date;
  status: 'permit' | 'challenge' | 'deny';
  responseTime: number;
}

export interface APIResponse {
  status: 'permit' | 'challenge' | 'deny';
  message: string;
  requestId: string;
  timestamp: Date;
  responseTime: number;
  challengeRequired?: boolean;
}