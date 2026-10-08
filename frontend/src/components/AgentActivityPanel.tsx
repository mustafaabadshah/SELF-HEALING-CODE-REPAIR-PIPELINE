import React from 'react';
import { Bot, Shield, Wrench, Clock, Coins, CheckCircle2 } from 'lucide-react';
import { AttemptSummary } from '../types';
import { CriticVerdictBadge } from './StatusBadge';

interface AgentActivityPanelProps {
  latestAttempt?: AttemptSummary;
  coderModel?: string;
  criticModel?: string;
  isStreaming?: boolean;
}

export const AgentActivityPanel: React.FC<AgentActivityPanelProps> = ({
  latestAttempt,
  coderModel = 'openai/gpt-oss-120b',
  criticModel = 'openai/gpt-oss-20b',
  isStreaming,
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Coder Card */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4">
        <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-md bg-indigo-950/80 border border-indigo-800/50 flex items-center justify-center text-indigo-400">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-zinc-100">Coder Agent</h3>
              <p className="text-[11px] font-mono text-zinc-400">Model: {coderModel}</p>
            </div>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
            {isStreaming ? 'THINKING / ACTING' : 'READY'}
          </span>
        </div>

        <div className="mt-3 space-y-2.5 text-xs">
          <div>
            <span className="text-zinc-400 font-mono block mb-1">Current Hypothesis:</span>
            <p className="text-zinc-200 bg-zinc-950/70 p-2.5 rounded border border-zinc-800/80 font-mono leading-relaxed">
              {latestAttempt?.hypothesis || 'Awaiting initial failure diagnosis...'}
            </p>
          </div>

          <div className="flex items-center justify-between text-zinc-400 font-mono text-[11px] pt-1 border-t border-zinc-800/50">
            <span className="flex items-center gap-1">
              <Wrench className="w-3.5 h-3.5 text-indigo-400" />
              Tools: apply_patch, read_file
            </span>
            <span className="flex items-center gap-1">
              <Coins className="w-3.5 h-3.5 text-amber-400" />
              Tokens: {(latestAttempt?.input_tokens || 0) + (latestAttempt?.output_tokens || 0)}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-emerald-400" />
              Latency: {latestAttempt?.latency_ms || 0}ms
            </span>
          </div>
        </div>
      </div>

      {/* Critic Card */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4">
        <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-md bg-purple-950/80 border border-purple-800/50 flex items-center justify-center text-purple-400">
              <Shield className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-zinc-100">Critic Agent</h3>
              <p className="text-[11px] font-mono text-zinc-400">Model: {criticModel}</p>
            </div>
          </div>
          {latestAttempt ? (
            <CriticVerdictBadge verdict={latestAttempt.critic_verdict} />
          ) : (
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-400">
              PENDING
            </span>
          )}
        </div>

        <div className="mt-3 space-y-2.5 text-xs">
          <div>
            <span className="text-zinc-400 font-mono block mb-1">Root Cause & Guidance:</span>
            <div className="text-zinc-200 bg-zinc-950/70 p-2.5 rounded border border-zinc-800/80 font-mono leading-relaxed max-h-28 overflow-y-auto">
              {latestAttempt?.critic_analysis || 'Awaiting test sandbox results for evaluation...'}
            </div>
          </div>

          <div className="flex items-center justify-between text-zinc-400 font-mono text-[11px] pt-1 border-t border-zinc-800/50">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              Confidence: {latestAttempt?.critic_confidence ? `${Math.round(latestAttempt.critic_confidence * 100)}%` : 'N/A'}
            </span>
            <span>Target: {latestAttempt?.target_passed ? 'PASS' : 'FAIL'}</span>
            <span>Regression: {latestAttempt?.regression_passed ? 'PASS' : 'FAIL'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
