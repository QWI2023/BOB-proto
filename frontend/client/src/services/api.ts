import { APIRequest, APIResponse, User } from '../types';

// Mock API service to simulate backend responses
class APIService {
  private static instance: APIService;
  private requests: APIRequest[] = [];

  static getInstance(): APIService {
    if (!APIService.instance) {
      APIService.instance = new APIService();
    }
    return APIService.instance;
  }

  async login(username: string, password: string): Promise<User> {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock authentication - in real app, this would call backend
    if (username && password) {
      const roles = ['Admin', 'Employee', 'Auditor', 'Vendor', 'Guest', 'Service', 'Customer'];
      const randomRole = roles[Math.floor(Math.random() * roles.length)];
      
      return {
        id: Math.random().toString(36).substring(7),
        username,
        role: randomRole,
        token: `token_${Math.random().toString(36).substring(7)}`
      };
    }
    
    throw new Error('Invalid credentials');
  }

  async sendAPIRequest(request: Omit<APIRequest, 'id' | 'timestamp' | 'status' | 'responseTime'>): Promise<APIResponse> {
    // Simulate processing delay
    const responseTime = Math.floor(Math.random() * 500) + 100;
    await new Promise(resolve => setTimeout(resolve, responseTime));

    // Mock decision logic based on request type and values
    let status: 'permit' | 'challenge' | 'deny';
    let message: string;

    // Simulate backend decision logic
    const random = Math.random();
    if (request.type === 'transaction' && request.amount && request.amount > 10000) {
      status = random > 0.7 ? 'deny' : 'challenge';
      message = status === 'deny' ? 'High-value transaction denied by risk policy' : 'Additional verification required for high-value transaction';
    } else if (request.type === 'logs' && request.geoLocation?.toLowerCase().includes('restricted')) {
      status = 'deny';
      message = 'Access denied from restricted geographical location';
    } else if (random > 0.8) {
      status = 'challenge';
      message = 'Anomalous behavior detected - MFA required';
    } else if (random > 0.9) {
      status = 'deny';
      message = 'Request denied by security policy';
    } else {
      status = 'permit';
      message = 'Request approved - all security checks passed';
    }

    const response: APIResponse = {
      status,
      message,
      requestId: `req_${Math.random().toString(36).substring(7)}`,
      timestamp: new Date(),
      responseTime,
      challengeRequired: status === 'challenge'
    };

    // Store request in history
    const apiRequest: APIRequest = {
      id: response.requestId,
      ...request,
      timestamp: new Date(),
      status,
      responseTime
    };

    this.requests.unshift(apiRequest);

    return response;
  }

  getRequestHistory(): APIRequest[] {
    return [...this.requests];
  }
}

export default APIService.getInstance();