// ===== 模型配置常量 =====

export const MODEL_PROVIDERS = ['openai', 'anthropic', 'ollama'] as const;

export const DEFAULT_MODELS: Record<string, string> = {
  openai: 'gpt-4o',
  anthropic: 'claude-sonnet-4-6',
  ollama: 'qwen2.5:7b',
} as const;

export const MODEL_TIERS = {
  cheap: {
    openai: 'gpt-4o-mini',
    anthropic: 'claude-haiku-4-5',
    ollama: 'qwen2.5:3b',
  },
  standard: {
    openai: 'gpt-4o',
    anthropic: 'claude-sonnet-4-6',
    ollama: 'qwen2.5:7b',
  },
  premium: {
    openai: 'gpt-4o',
    anthropic: 'claude-opus-4-8',
    ollama: 'qwen2.5:72b',
  },
} as const;

export const AGENT_ROLES = [
  { value: 'researcher', label: '🔍 研究员', description: '搜索信息、分析数据、生成报告' },
  { value: 'coder', label: '💻 程序员', description: '编写代码、调试、代码审查' },
  { value: 'writer', label: '✍️ 写作者', description: '长文创作、编辑润色、翻译' },
  { value: 'organizer', label: '🗂️ 整理师', description: '分类归档、日程管理、待办追踪' },
  { value: 'general', label: '🤖 通用助理', description: '综合任务处理' },
] as const;

export const COLLABORATION_MODES = [
  { value: 'pipeline', label: '流水线', description: 'A → B → C 顺序执行' },
  { value: 'parallel', label: '并行', description: '多 Agent 同时执行后合并' },
  { value: 'debate', label: '辩论', description: '多 Agent 讨论达成共识' },
] as const;
