// ===== API 路由常量 =====

export const API_PREFIX = '/api/v1';

export const ROUTES = {
  auth: {
    login: '/auth/login',
    register: '/auth/register',
    refresh: '/auth/refresh',
    me: '/auth/me',
  },
  tasks: {
    base: '/tasks',
    detail: (id: string) => `/tasks/${id}`,
    cancel: (id: string) => `/tasks/${id}/cancel`,
    stream: (id: string) => `/tasks/${id}/stream`,
    templates: '/tasks/templates',
  },
  agents: {
    base: '/agents',
    detail: (id: string) => `/agents/${id}`,
    execute: (id: string) => `/agents/${id}/execute`,
  },
  tools: {
    base: '/tools',
    detail: (id: string) => `/tools/${id}`,
    test: (id: string) => `/tools/${id}/test`,
  },
  memory: {
    base: '/memory',
    search: '/memory/search',
    documents: '/memory/documents',
    stats: '/memory/stats',
  },
} as const;
