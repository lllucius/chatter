/**
 * Tests for Chatter SDK Service
 */

import { ChatterSDK } from '../chatter-sdk';
import { UserLogin, UserCreate, ChatRequest } from '../../sdk';

// Mock the SDK modules
jest.mock('../../sdk', () => ({
  Configuration: jest.fn(),
  AuthenticationApi: jest.fn(),
  AnalyticsApi: jest.fn(),
  ABTestingApi: jest.fn(),
  ChatApi: jest.fn(),
  DocumentsApi: jest.fn(),
  ProfilesApi: jest.fn(),
  PromptsApi: jest.fn(),
  AgentsApi: jest.fn(),
  ToolServersApi: jest.fn(),
  DataManagementApi: jest.fn(),
  PluginsApi: jest.fn(),
  HealthApi: jest.fn(),
  JobsApi: jest.fn(),
  ModelRegistryApi: jest.fn(),
}));

// Mock localStorage
const mockLocalStorage = {
  storage: {} as Record<string, string>,
  getItem: jest.fn((key: string) => mockLocalStorage.storage[key] || null),
  setItem: jest.fn((key: string, value: string) => {
    mockLocalStorage.storage[key] = value;
  }),
  removeItem: jest.fn((key: string) => {
    delete mockLocalStorage.storage[key];
  }),
  clear: jest.fn(() => {
    mockLocalStorage.storage = {};
  })
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

describe('ChatterSDK', () => {
  let chatterSDK: ChatterSDK;

  beforeEach(() => {
    chatterSDK = new ChatterSDK();
    mockLocalStorage.clear();
    jest.clearAllMocks();
  });

  describe('Initialization', () => {
    test('should initialize with default configuration', () => {
      expect(chatterSDK).toBeDefined();
      expect(chatterSDK.isAuthenticated()).toBe(false);
    });

    test('should initialize with custom base URL', () => {
      const customSDK = new ChatterSDK('https://custom.api.com');
      expect(customSDK).toBeDefined();
    });

    test('should load stored authentication on initialization', () => {
      const storedAuth = {
        token: 'stored-token',
        expiresAt: Date.now() + 3600000,
        updatedAt: Date.now()
      };
      mockLocalStorage.setItem('chatter_auth', JSON.stringify(storedAuth));
      
      const newSDK = new ChatterSDK();
      expect(newSDK.isAuthenticated()).toBe(true);
    });

    test('should ignore expired stored tokens', () => {
      const expiredAuth = {
        token: 'expired-token',
        expiresAt: Date.now() - 3600000, // Expired 1 hour ago
        updatedAt: Date.now() - 3600000
      };
      mockLocalStorage.setItem('chatter_auth', JSON.stringify(expiredAuth));
      
      const newSDK = new ChatterSDK();
      expect(newSDK.isAuthenticated()).toBe(false);
    });

    test('should migrate legacy token storage', () => {
      mockLocalStorage.setItem('chatter_token', 'legacy-token');
      
      const newSDK = new ChatterSDK();
      
      // Should migrate and clean up legacy storage
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('chatter_token');
      expect(newSDK.isAuthenticated()).toBe(true);
    });
  });

  describe('Authentication Management', () => {
    test('should set authentication token', () => {
      const token = 'test-auth-token';
      chatterSDK.setAuth(token);
      
      expect(chatterSDK.isAuthenticated()).toBe(true);
    });

    test('should set authentication token with expiry', () => {
      const token = 'test-auth-token';
      const expiresAt = Date.now() + 3600000; // 1 hour
      
      chatterSDK.setAuth(token, expiresAt);
      
      expect(chatterSDK.isAuthenticated()).toBe(true);
    });

    test('should clear authentication', () => {
      chatterSDK.setAuth('test-token');
      expect(chatterSDK.isAuthenticated()).toBe(true);
      
      chatterSDK.clearAuth();
      expect(chatterSDK.isAuthenticated()).toBe(false);
    });

    test('should persist authentication to localStorage', () => {
      const token = 'persist-token';
      chatterSDK.setAuth(token);
      
      const stored = JSON.parse(mockLocalStorage.getItem('chatter_auth') || '{}');
      expect(stored.token).toBe(token);
      expect(stored.updatedAt).toBeDefined();
    });

    test('should get authentication headers', () => {
      const token = 'auth-header-token';
      chatterSDK.setAuth(token);
      
      const headers = chatterSDK.getAuthHeaders();
      expect(headers.Authorization).toBe(`Bearer ${token}`);
    });

    test('should return empty headers when not authenticated', () => {
      const headers = chatterSDK.getAuthHeaders();
      expect(headers.Authorization).toBeUndefined();
    });
  });

  describe('Token Expiry Management', () => {
    test('should detect expired tokens', () => {
      const token = 'expiring-token';
      const expiredTime = Date.now() - 1000; // 1 second ago
      
      chatterSDK.setAuth(token, expiredTime);
      
      expect(chatterSDK.isAuthenticated()).toBe(false);
    });

    test('should handle tokens without expiry as non-expiring', () => {
      const token = 'no-expiry-token';
      chatterSDK.setAuth(token); // No expiry provided
      
      expect(chatterSDK.isAuthenticated()).toBe(true);
    });

    test('should check if token is expiring soon', () => {
      const token = 'soon-expiring-token';
      const soonExpiry = Date.now() + 30000; // 30 seconds
      
      chatterSDK.setAuth(token, soonExpiry);
      
      const isExpiringSoon = chatterSDK.isTokenExpiringSoon();
      expect(isExpiringSoon).toBe(true);
    });

    test('should not flag non-expiring tokens as expiring soon', () => {
      const token = 'no-expiry-token';
      chatterSDK.setAuth(token);
      
      const isExpiringSoon = chatterSDK.isTokenExpiringSoon();
      expect(isExpiringSoon).toBe(false);
    });
  });

  describe('Login Flow', () => {
    test('should perform login successfully', async () => {
      const mockLoginResponse = {
        access_token: 'login-success-token',
        token_type: 'bearer',
        expires_in: 3600
      };

      // Mock the authentication API
      const mockLogin = jest.fn().mockResolvedValue({ data: mockLoginResponse });
      (chatterSDK as any).auth = { loginForAccessToken: mockLogin };

      const credentials: UserLogin = {
        username: 'testuser',
        password: 'testpass'
      };

      const result = await chatterSDK.login(credentials);

      expect(mockLogin).toHaveBeenCalledWith(credentials);
      expect(result).toEqual(mockLoginResponse);
      expect(chatterSDK.isAuthenticated()).toBe(true);
    });

    test('should handle login failure', async () => {
      const mockError = new Error('Invalid credentials');
      const mockLogin = jest.fn().mockRejectedValue(mockError);
      (chatterSDK as any).auth = { loginForAccessToken: mockLogin };

      const credentials: UserLogin = {
        username: 'baduser',
        password: 'badpass'
      };

      await expect(chatterSDK.login(credentials)).rejects.toThrow('Invalid credentials');
      expect(chatterSDK.isAuthenticated()).toBe(false);
    });

    test('should perform logout', async () => {
      // Set initial authentication
      chatterSDK.setAuth('logout-test-token');
      expect(chatterSDK.isAuthenticated()).toBe(true);

      // Mock logout API
      const mockLogout = jest.fn().mockResolvedValue({ data: { success: true } });
      (chatterSDK as any).auth = { logout: mockLogout };

      await chatterSDK.logout();

      expect(mockLogout).toHaveBeenCalled();
      expect(chatterSDK.isAuthenticated()).toBe(false);
    });
  });

  describe('Registration Flow', () => {
    test('should perform registration successfully', async () => {
      const mockRegisterResponse = {
        id: 'user-123',
        username: 'newuser',
        email: 'new@example.com'
      };

      const mockRegister = jest.fn().mockResolvedValue({ data: mockRegisterResponse });
      (chatterSDK as any).auth = { register: mockRegister };

      const userData: UserCreate = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'newpass123'
      };

      const result = await chatterSDK.register(userData);

      expect(mockRegister).toHaveBeenCalledWith(userData);
      expect(result).toEqual(mockRegisterResponse);
    });

    test('should handle registration failure', async () => {
      const mockError = new Error('Username already exists');
      const mockRegister = jest.fn().mockRejectedValue(mockError);
      (chatterSDK as any).auth = { register: mockRegister };

      const userData: UserCreate = {
        username: 'existinguser',
        email: 'existing@example.com',
        password: 'pass123'
      };

      await expect(chatterSDK.register(userData)).rejects.toThrow('Username already exists');
    });
  });

  describe('Chat Operations', () => {
    beforeEach(() => {
      chatterSDK.setAuth('chat-test-token');
    });

    test('should send chat message', async () => {
      const mockChatResponse = {
        id: 'msg-123',
        content: 'Hello, world!',
        conversation_id: 'conv-456'
      };

      const mockSendMessage = jest.fn().mockResolvedValue({ data: mockChatResponse });
      (chatterSDK as any).chat = { sendMessage: mockSendMessage };

      const request: ChatRequest = {
        message: 'Hello',
        conversation_id: 'conv-456'
      };

      const result = await chatterSDK.sendChatMessage(request);

      expect(mockSendMessage).toHaveBeenCalledWith(request);
      expect(result).toEqual(mockChatResponse);
    });

    test('should get chat history', async () => {
      const mockHistory = [
        { id: 'msg-1', content: 'First message' },
        { id: 'msg-2', content: 'Second message' }
      ];

      const mockGetHistory = jest.fn().mockResolvedValue({ data: mockHistory });
      (chatterSDK as any).chat = { getChatHistory: mockGetHistory };

      const conversationId = 'conv-123';
      const result = await chatterSDK.getChatHistory(conversationId);

      expect(mockGetHistory).toHaveBeenCalledWith(conversationId, undefined, undefined);
      expect(result).toEqual(mockHistory);
    });

    test('should get chat history with pagination', async () => {
      const mockHistory = [{ id: 'msg-1', content: 'Paginated message' }];
      const mockGetHistory = jest.fn().mockResolvedValue({ data: mockHistory });
      (chatterSDK as any).chat = { getChatHistory: mockGetHistory };

      const conversationId = 'conv-123';
      const limit = 10;
      const offset = 20;

      const result = await chatterSDK.getChatHistory(conversationId, limit, offset);

      expect(mockGetHistory).toHaveBeenCalledWith(conversationId, limit, offset);
      expect(result).toEqual(mockHistory);
    });
  });

  describe('Document Operations', () => {
    beforeEach(() => {
      chatterSDK.setAuth('doc-test-token');
    });

    test('should upload document', async () => {
      const mockUploadResponse = {
        id: 'doc-123',
        filename: 'test.pdf',
        status: 'uploaded'
      };

      const mockUpload = jest.fn().mockResolvedValue({ data: mockUploadResponse });
      (chatterSDK as any).documents = { uploadDocument: mockUpload };

      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      const result = await chatterSDK.uploadDocument(file);

      expect(mockUpload).toHaveBeenCalled();
      expect(result).toEqual(mockUploadResponse);
    });

    test('should list documents', async () => {
      const mockDocuments = [
        { id: 'doc-1', filename: 'doc1.pdf' },
        { id: 'doc-2', filename: 'doc2.txt' }
      ];

      const mockList = jest.fn().mockResolvedValue({ data: { documents: mockDocuments } });
      (chatterSDK as any).documents = { listDocuments: mockList };

      const result = await chatterSDK.listDocuments();

      expect(mockList).toHaveBeenCalled();
      expect(result.documents).toEqual(mockDocuments);
    });
  });

  describe('Configuration Management', () => {
    test('should get current base URL', () => {
      const baseURL = chatterSDK.getBaseURL();
      expect(typeof baseURL).toBe('string');
      expect(baseURL.startsWith('http')).toBe(true);
    });

    test('should update configuration', () => {
      const newBaseURL = 'https://new-api.example.com';
      chatterSDK.updateConfig({ basePath: newBaseURL });
      
      expect(chatterSDK.getBaseURL()).toBe(newBaseURL);
    });
  });

  describe('Error Handling', () => {
    test('should handle API errors gracefully', async () => {
      const apiError = {
        response: {
          status: 401,
          data: { detail: 'Unauthorized' }
        }
      };

      const mockFailedCall = jest.fn().mockRejectedValue(apiError);
      (chatterSDK as any).auth = { loginForAccessToken: mockFailedCall };

      const credentials: UserLogin = {
        username: 'testuser',
        password: 'wrongpass'
      };

      await expect(chatterSDK.login(credentials)).rejects.toMatchObject(apiError);
    });

    test('should handle network errors', async () => {
      const networkError = new Error('Network Error');
      const mockFailedCall = jest.fn().mockRejectedValue(networkError);
      (chatterSDK as any).health = { getHealthStatus: mockFailedCall };

      await expect(chatterSDK.checkHealth()).rejects.toThrow('Network Error');
    });
  });

  describe('Health Check', () => {
    test('should check API health', async () => {
      const mockHealthResponse = {
        status: 'healthy',
        version: '1.0.0',
        timestamp: new Date().toISOString()
      };

      const mockHealthCheck = jest.fn().mockResolvedValue({ data: mockHealthResponse });
      (chatterSDK as any).health = { getHealthStatus: mockHealthCheck };

      const result = await chatterSDK.checkHealth();

      expect(mockHealthCheck).toHaveBeenCalled();
      expect(result).toEqual(mockHealthResponse);
    });
  });

  describe('Profile Management', () => {
    beforeEach(() => {
      chatterSDK.setAuth('profile-test-token');
    });

    test('should get user profile', async () => {
      const mockProfile = {
        id: 'user-123',
        username: 'testuser',
        email: 'test@example.com',
        preferences: { theme: 'dark' }
      };

      const mockGetProfile = jest.fn().mockResolvedValue({ data: mockProfile });
      (chatterSDK as any).profiles = { getCurrentProfile: mockGetProfile };

      const result = await chatterSDK.getProfile();

      expect(mockGetProfile).toHaveBeenCalled();
      expect(result).toEqual(mockProfile);
    });

    test('should update user profile', async () => {
      const updatedProfile = {
        username: 'updateduser',
        preferences: { theme: 'light', notifications: true }
      };

      const mockUpdateProfile = jest.fn().mockResolvedValue({ data: updatedProfile });
      (chatterSDK as any).profiles = { updateProfile: mockUpdateProfile };

      const result = await chatterSDK.updateProfile(updatedProfile);

      expect(mockUpdateProfile).toHaveBeenCalledWith(updatedProfile);
      expect(result).toEqual(updatedProfile);
    });
  });

  describe('Storage Management', () => {
    test('should handle corrupted stored data', () => {
      mockLocalStorage.setItem('chatter_auth', 'invalid-json{');
      
      // Should not throw error, should handle gracefully
      const newSDK = new ChatterSDK();
      expect(newSDK.isAuthenticated()).toBe(false);
    });

    test('should handle missing localStorage', () => {
      // Mock localStorage as undefined (some environments)
      const originalLS = window.localStorage;
      (window as any).localStorage = undefined;
      
      expect(() => new ChatterSDK()).not.toThrow();
      
      // Restore
      (window as any).localStorage = originalLS;
    });
  });

  describe('Event Handling', () => {
    test('should emit authentication events', () => {
      const loginHandler = jest.fn();
      const logoutHandler = jest.fn();
      
      chatterSDK.on('login', loginHandler);
      chatterSDK.on('logout', logoutHandler);
      
      chatterSDK.setAuth('event-test-token');
      expect(loginHandler).toHaveBeenCalled();
      
      chatterSDK.clearAuth();
      expect(logoutHandler).toHaveBeenCalled();
    });

    test('should remove event listeners', () => {
      const handler = jest.fn();
      
      chatterSDK.on('login', handler);
      chatterSDK.off('login', handler);
      
      chatterSDK.setAuth('test-token');
      expect(handler).not.toHaveBeenCalled();
    });
  });
});