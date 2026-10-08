import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, RefreshCw, Clock, UserCheck } from 'lucide-react';
import { RepairStatus, CriticVerdict } from '../types';

interface StatusBadgeProps {
  status: RepairStatus | string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3.5 py-1.5 text-sm',
  }[size];

  switch (status) {
    case 'SUCCESS':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 ${sizeClasses}`}>
          <CheckCircle2 className="w-3.5 h-3.5" />
          SUCCESS
        </span>
      );
    case 'SELF_CORRECTING':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-amber-950/80 text-amber-400 border border-amber-800/60 ${sizeClasses}`}>
          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          SELF-CORRECTING
        </span>
      );
    case 'RUNNING':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-blue-950/80 text-blue-400 border border-blue-800/60 ${sizeClasses}`}>
          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          RUNNING
        </span>
      );
    case 'HUMAN_REVIEW':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-purple-950/80 text-purple-400 border border-purple-800/60 ${sizeClasses}`}>
          <UserCheck className="w-3.5 h-3.5" />
          HUMAN REVIEW
        </span>
      );
    case 'FAILED':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-rose-950/80 text-rose-400 border border-rose-800/60 ${sizeClasses}`}>
          <XCircle className="w-3.5 h-3.5" />
          FAILED
        </span>
      );
    case 'QUEUED':
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-zinc-900 text-zinc-400 border border-zinc-800 ${sizeClasses}`}>
          <Clock className="w-3.5 h-3.5" />
          QUEUED
        </span>
      );
  }
};

export const CriticVerdictBadge: React.FC<{ verdict: CriticVerdict | string }> = ({ verdict }) => {
  switch (verdict) {
    case 'PASS':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
          <CheckCircle2 className="w-3 h-3" /> PASS
        </span>
      );
    case 'REVISE':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono font-semibold bg-amber-950 text-amber-400 border border-amber-800">
          <RefreshCw className="w-3 h-3" /> REVISE
        </span>
      );
    case 'ESCALATE':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono font-semibold bg-rose-950 text-rose-400 border border-rose-800">
          <AlertTriangle className="w-3 h-3" /> ESCALATE
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono bg-zinc-800 text-zinc-400">
          {verdict}
        </span>
      );
  }
};

export const TestBadge: React.FC<{ passed: boolean; label?: string }> = ({ passed, label }) => {
  return passed ? (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono font-semibold bg-emerald-950/70 text-emerald-400 border border-emerald-800/50">
      <CheckCircle2 className="w-3 h-3" /> {label || 'PASS'}
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono font-semibold bg-rose-950/70 text-rose-400 border border-rose-800/50">
      <XCircle className="w-3 h-3" /> {label || 'FAIL'}
    </span>
  );
};
