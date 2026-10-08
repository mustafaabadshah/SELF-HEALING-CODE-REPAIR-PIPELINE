import {
  RepairDetail,
  CreateRepairPayload,
  DashboardMetrics,
  DiffResponse,
} from '../types';

const API_BASE = '/api';

export async function createRepair(payload: CreateRepairPayload): Promise<{ repair_id: string; status: string }> {
  const res = await fetch(`${API_BASE}/repairs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to create repair' }));
    throw new Error(err.detail || 'Failed to create repair');
  }
  return res.json();
}

export async function getRepair(id: string): Promise<RepairDetail> {
  const res = await fetch(`${API_BASE}/repairs/${id}`);
  if (!res.ok) throw new Error('Failed to fetch repair');
  return res.json();
}

export async function listRepairs(limit = 50): Promise<RepairDetail[]> {
  const res = await fetch(`${API_BASE}/repairs?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to list repairs');
  return res.json();
}

export async function getRepairDiff(id: string): Promise<DiffResponse> {
  const res = await fetch(`${API_BASE}/repairs/${id}/diff`);
  if (!res.ok) throw new Error('Failed to fetch diff');
  return res.json();
}

export async function getMetrics(): Promise<DashboardMetrics> {
  const res = await fetch(`${API_BASE}/metrics`);
  if (!res.ok) throw new Error('Failed to fetch metrics');
  return res.json();
}

export async function submitEscalationDecision(
  id: string,
  decision: 'APPROVE_PATCH' | 'REJECT_PATCH' | 'RESET',
  comment = ''
): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/repairs/${id}/escalation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decision, comment }),
  });
  if (!res.ok) throw new Error('Failed to submit escalation decision');
  return res.json();
}

export async function preloadDemoData(): Promise<CreateRepairPayload> {
  const res = await fetch(`${API_BASE}/demo/preload`);
  if (!res.ok) throw new Error('Failed to load demo scenario');
  return res.json();
}

export async function fetchPresets(): Promise<import('../types').PresetItem[]> {
  const res = await fetch(`${API_BASE}/presets`);
  if (!res.ok) throw new Error('Failed to load presets');
  return res.json();
}

export async function scanDirectory(directoryPath: string): Promise<import('../types').ScanDirectoryResponse> {
  const res = await fetch(`${API_BASE}/workspace/scan-directory`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ directory_path: directoryPath }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to scan directory' }));
    throw new Error(err.detail || 'Failed to scan directory');
  }
  return res.json();
}

