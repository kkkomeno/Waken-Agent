// ===== 用户类型 =====

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: UserRole;
  preferences: UserPreferences;
  createdAt: string;
}

export type UserRole = 'admin' | 'user';

export interface UserPreferences {
  defaultModel: string;
  language: string;
  notifications: NotificationPreferences;
}

export interface NotificationPreferences {
  taskComplete: boolean;
  agentRequest: boolean;
  dailyReport: boolean;
  pushEnabled: boolean;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface LoginResult {
  accessToken: string;
  refreshToken: string;
  user: User;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}
