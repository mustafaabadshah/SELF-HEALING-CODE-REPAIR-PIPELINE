export type RepairStatus =
  | 'QUEUED'
  | 'RUNNING'
  | 'SELF_CORRECTING'
  | 'SUCCESS'
  | 'FAILED'
  | 'HUMAN_REVIEW';

export type CriticVerdict = 'PASS' | 'REVISE' | 'ESCALATE';

export interface AttemptSummary {
  id: string;
  attempt_number: number;
  hypothesis: string;
  diff: string;
  target_passed: boolean;
  regression_passed: boolean;
  critic_verdict: CriticVerdict;
  critic_analysis: string;
  critic_confidence?: number;
  failure_type: string;
  latency_ms: number;
  input_tokens: number;
  output_tokens: number;
  created_at: string;
}

export interface RepairDetail {
  id: string;
  status: RepairStatus;
  source_file: string;
  test_file: string;
  target_test: string;
  max_attempts: number;
  current_attempt: number;
  trace_id: string;
  trace_url?: string;
  error_message?: string;
  final_diff?: string;
  created_at: string;
  updated_at: string;
  attempts: AttemptSummary[];
}

export interface DiffResponse {
  repair_id: string;
  diff: string;
  files_changed: number;
  lines_added: number;
  lines_removed: number;
}

export interface DashboardMetrics {
  total_repairs: number;
  successful_repairs: number;
  failed_repairs: number;
  escalations: number;
  average_attempts: number;
  average_repair_time_ms: number;
  regression_rate: number;
  total_tokens: number;
  average_latency_ms: number;
}

export interface RepairEvent {
  repair_id: string;
  event_type: string;
  payload: Record<string, any>;
  timestamp: string;
}

export interface RegressionFilePayload {
  filename: string;
  content: string;
}

export interface CreateRepairPayload {
  source_file: string;
  source_content: string;
  test_file: string;
  test_content: string;
  target_test: string;
  regression_tests: RegressionFilePayload[];
  max_attempts: number;
  use_mock?: boolean;
}

export interface ScannedFile {
  filename: string;
  content: string;
  test_cases: string[];
}

export interface ScanDirectoryResponse {
  directory_path: string;
  source_files: ScannedFile[];
  test_files: ScannedFile[];
}

export interface PresetItem {
  id: string;
  title: string;
  category: string;
  badge: string;
  description: string;
  layman_story: string;
  source_file: string;
  source_content: string;
  test_file: string;
  test_content: string;
  target_test: string;
  regression_tests: RegressionFilePayload[];
  max_attempts: number;
}

