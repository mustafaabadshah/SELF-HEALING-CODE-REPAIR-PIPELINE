import React from 'react';
import { AttemptSummary } from '../types';
import { CriticVerdictBadge, TestBadge } from './StatusBadge';
import { CheckCircle2, Clock, Coins } from 'lucide-react';

interface AttemptTimelineProps {
  attempts: AttemptSummary[];
}

export const AttemptTimeline: React.FC<AttemptTimelineProps> = ({ attempts }) => {
  if (!attempts || attempts.length === 0) {
    return (
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-6 text-center text-zinc-400 font-mono text-xs">
        No repair attempts recorded yet. Pipeline is executing...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {attempts.map((att, idx) => {
        const isSuccess = att.target_passed && att.regression_passed && att.critic_verdict === 'PASS';

        return (
          <div
            key={att.id || idx}
            className={`rounded-lg border p-4 transition-all ${
              isSuccess
                ? 'bg-emerald-950/20 border-emerald-800/60'
                : 'bg-zinc-900/70 border-zinc-800'
            }`}
          >
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-zinc-800 flex-wrap gap-2">
              <div className="flex items-center gap-2.5">
                <span className="w-6 h-6 rounded bg-zinc-800 text-zinc-200 font-mono text-xs font-bold flex items-center justify-center border border-zinc-700">
                  {att.attempt_number}
                </span>
                <span className="font-semibold text-zinc-100 text-sm">
                  Attempt {att.attempt_number} {isSuccess && '— Final Solved'}
                </span>
                {isSuccess && (
                  <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                    PASS VERIFIED
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2">
                <CriticVerdictBadge verdict={att.critic_verdict} />
                <span className="text-[11px] font-mono text-zinc-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {att.latency_ms}ms
                </span>
              </div>
            </div>

            {/* Stepped breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 my-3 text-xs font-mono">
              <div className="bg-zinc-950/70 p-2.5 rounded border border-zinc-800">
                <span className="text-zinc-400 block text-[10px] uppercase">Coder Hypothesis</span>
                <p className="text-zinc-200 mt-1 line-clamp-2">{att.hypothesis}</p>
              </div>

              <div className="bg-zinc-950/70 p-2.5 rounded border border-zinc-800">
                <span className="text-zinc-400 block text-[10px] uppercase">Target Test</span>
                <div className="mt-1">
                  <TestBadge passed={att.target_passed} />
                </div>
              </div>

              <div className="bg-zinc-950/70 p-2.5 rounded border border-zinc-800">
                <span className="text-zinc-400 block text-[10px] uppercase">Regression Suite</span>
                <div className="mt-1">
                  <TestBadge
                    passed={att.regression_passed}
                    label={att.regression_passed ? 'NO REGRESSION' : 'REGRESSION DETECTED'}
                  />
                </div>
              </div>

              <div className="bg-zinc-950/70 p-2.5 rounded border border-zinc-800">
                <span className="text-zinc-400 block text-[10px] uppercase">Critic Verdict</span>
                <p className="text-zinc-300 mt-1 font-semibold text-xs">
                  {att.critic_verdict}: {att.failure_type || 'Evaluated'}
                </p>
              </div>
            </div>

            {/* Critic feedback */}
            <div className="bg-zinc-950/90 p-3 rounded border border-zinc-800/80 text-xs font-mono">
              <span className="text-purple-400 block mb-1 text-[11px] uppercase font-semibold">
                Critic Analysis & Feedback:
              </span>
              <p className="text-zinc-300 whitespace-pre-wrap leading-relaxed">
                {att.critic_analysis}
              </p>
            </div>

            <div className="mt-2.5 flex items-center justify-between text-[11px] font-mono text-zinc-400">
              <span className="flex items-center gap-1">
                <Coins className="w-3 h-3 text-amber-400" />
                Tokens: {att.input_tokens + att.output_tokens} (In: {att.input_tokens}, Out: {att.output_tokens})
              </span>
              <span>Diff Length: {att.diff ? att.diff.split('\n').length : 0} lines</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
