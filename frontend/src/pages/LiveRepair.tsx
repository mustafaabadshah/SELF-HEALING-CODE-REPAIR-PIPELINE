import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ExternalLink,
  RefreshCw,
  AlertTriangle,
  UserCheck,
  CheckCircle2,
  XCircle,
  RotateCcw,
  Activity,
  Terminal,
  Sparkles,
  Info,
} from 'lucide-react';
import { useRepairStream } from '../hooks/useRepairStream';
import { submitEscalationDecision } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { GraphFlowVisualizer } from '../components/GraphFlowVisualizer';
import { AgentActivityPanel } from '../components/AgentActivityPanel';
import { CodeView } from '../components/CodeView';
import { TestResultsPanel } from '../components/TestResultsPanel';
import { AttemptTimeline } from '../components/AttemptTimeline';

export const LiveRepair: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { repair, events, activeNode, isConnected, isLoading, refreshData } = useRepairStream(id);

  const [escalating, setEscalating] = useState(false);
  const [comment, setComment] = useState('');
  const [showEvents, setShowEvents] = useState(false);

  const handleEscalation = async (decision: 'APPROVE_PATCH' | 'REJECT_PATCH' | 'RESET') => {
    if (!id) return;
    try {
      setEscalating(true);
      await submitEscalationDecision(id, decision, comment);
      await refreshData();
    } catch (e: any) {
      alert(`Escalation failed: ${e.message}`);
    } finally {
      setEscalating(false);
    }
  };

  if (isLoading && !repair) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center">
        <RefreshCw className="w-8 h-8 mx-auto text-emerald-500 animate-spin mb-3" />
        <p className="text-zinc-400 font-mono text-sm">Connecting to repair workspace and streaming telemetry...</p>
      </div>
    );
  }

  if (!repair) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center">
        <AlertTriangle className="w-8 h-8 mx-auto text-rose-500 mb-3" />
        <p className="text-zinc-200 font-bold">Repair job not found.</p>
        <Link to="/" className="text-emerald-400 text-xs font-mono underline mt-2 block">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const latestAttempt = repair.attempts[repair.attempts.length - 1];
  const isHumanReview = repair.status === 'HUMAN_REVIEW';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Top Header Card */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-xs font-mono text-zinc-400">REPAIR RUN</span>
            <span className="font-mono text-base font-bold text-zinc-100">{repair.id}</span>
            <StatusBadge status={repair.status} />
            <span className="px-2.5 py-1 rounded text-xs font-mono bg-zinc-800 border border-zinc-700 text-zinc-300">
              ATTEMPT {repair.current_attempt || 1} / {repair.max_attempts}
            </span>
          </div>
          <p className="text-xs text-zinc-400 font-mono">
            Source: <span className="text-zinc-200 font-semibold">{repair.source_file}</span> | Target Test:{' '}
            <span className="text-zinc-200 font-semibold truncate">{repair.target_test}</span>
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {repair.trace_url ? (
            <a
              href={repair.trace_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-xs font-mono text-emerald-400 transition"
            >
              <span>LANGFUSE TRACE</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          ) : (
            <span className="text-xs font-mono text-zinc-400 px-2.5 py-1 rounded bg-zinc-950 border border-zinc-800">
              TRACE: {repair.trace_id}
            </span>
          )}

          <div className="flex items-center gap-1.5 text-xs font-mono text-zinc-400">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
            <span>{isConnected ? 'LIVE WS' : 'SYNCED'}</span>
          </div>
        </div>
      </div>

      {/* Layman Plain-English Live Explanation Banner */}
      <div className="bg-gradient-to-r from-zinc-900 via-zinc-900/90 to-zinc-900 border border-zinc-800 rounded-xl p-4 shadow-sm space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 font-mono">
              Plain-English Progress Story
            </span>
          </div>
          <span className="text-[11px] text-zinc-500 font-mono">Simplified Layman View</span>
        </div>

        {repair.status === 'SUCCESS' ? (
          <div className="flex items-start gap-3 bg-emerald-950/30 border border-emerald-800/50 rounded-lg p-3 text-xs text-emerald-200">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-bold text-emerald-300 block">🎉 The Code is Completely Repaired & Verified!</span>
              <p className="text-emerald-300/80 leading-relaxed">
                The bug in <code className="bg-emerald-950 px-1 py-0.5 rounded text-emerald-200 font-mono">{repair.source_file}</code> has been resolved. Crucially, both the failing target test <strong className="text-emerald-200">AND all existing regression tests</strong> passed with 100% success. The impartial Critic AI verified that no other features broke.
              </p>
            </div>
          </div>
        ) : repair.status === 'HUMAN_REVIEW' ? (
          <div className="flex items-start gap-3 bg-purple-950/30 border border-purple-800/50 rounded-lg p-3 text-xs text-purple-200">
            <UserCheck className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-bold text-purple-300 block">👤 Human Safety Check: Review Required</span>
              <p className="text-purple-300/80 leading-relaxed">
                The AI reached its limit of {repair.max_attempts} attempts without fully passing all tests. To protect your software from risky guesses, the system safely paused and escalated the latest proposed patch for your review below.
              </p>
            </div>
          </div>
        ) : latestAttempt && !latestAttempt.regression_passed && latestAttempt.target_passed ? (
          <div className="flex items-start gap-3 bg-amber-950/30 border border-amber-800/50 rounded-lg p-3 text-xs text-amber-200">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-bold text-amber-300 block">⚠️ Self-Healing in Progress: Regression Caught on Attempt {latestAttempt.attempt_number}!</span>
              <p className="text-amber-300/80 leading-relaxed">
                The AI's first guess solved the broken test, <strong className="text-amber-100">BUT it broke another existing feature</strong>! Unlike naive chatbots that would falsely declare success, this system detected the regression, discarded the bad code, and sent the Critic's diagnosis to the Coder for a corrected Attempt {latestAttempt.attempt_number + 1}.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex items-start gap-3 bg-zinc-950/60 border border-zinc-800/80 rounded-lg p-3 text-xs text-zinc-300">
            <Sparkles className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-bold text-zinc-200 block">
                🤖 Autonomous Multi-Agent Loop Working (Attempt {repair.current_attempt || 1} of {repair.max_attempts})
              </span>
              <p className="text-zinc-400 leading-relaxed">
                The Coder AI is operating inside an isolated sandbox container. It analyzes the error logs, makes a minimal code change, and verifies it with pytest. Watch the live graph below to see each agent turn!
              </p>
            </div>
          </div>
        )}
      </div>


      {isHumanReview && (
        <div className="bg-purple-950/40 border border-purple-800/80 rounded-lg p-5 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-md bg-purple-900/60 border border-purple-700 flex items-center justify-center text-purple-300">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-purple-200">
                Human Review Escalation Required
              </h3>
              <p className="text-xs text-purple-300/80">
                The agent pipeline reached maximum repair attempts without fully satisfying all test verification criteria.
              </p>
            </div>
          </div>

          <div className="bg-zinc-950/80 p-3 rounded border border-purple-900/50 text-xs font-mono text-zinc-300">
            <span className="text-purple-400 block mb-1 font-semibold">Critic Final Assessment:</span>
            {latestAttempt?.critic_analysis || 'Review required by engineer.'}
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
            <input
              type="text"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Optional engineer review comment..."
              className="bg-zinc-950 border border-purple-800/50 rounded px-3 py-1.5 text-xs font-mono text-zinc-200 flex-1 focus:outline-none"
            />

            <div className="flex items-center gap-2">
              <button
                disabled={escalating}
                onClick={() => handleEscalation('APPROVE_PATCH')}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-semibold transition"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>APPROVE PATCH</span>
              </button>
              <button
                disabled={escalating}
                onClick={() => handleEscalation('REJECT_PATCH')}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded bg-rose-600 hover:bg-rose-500 text-white font-mono text-xs font-semibold transition"
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>REJECT PATCH</span>
              </button>
              <button
                disabled={escalating}
                onClick={() => handleEscalation('RESET')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-mono text-xs transition"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>RESET</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Visual State Graph */}
      <GraphFlowVisualizer
        activeNode={activeNode}
        attempt={repair.current_attempt || 1}
        maxAttempts={repair.max_attempts}
        status={repair.status}
      />

      {/* Agents Activity */}
      <AgentActivityPanel
        latestAttempt={latestAttempt}
        isStreaming={repair.status === 'RUNNING' || repair.status === 'SELF_CORRECTING'}
      />

      {/* Code and Diff Viewer */}
      <CodeView
        originalCode=""
        currentCode=""
        diff={latestAttempt?.diff || repair.final_diff || ''}
        filename={repair.source_file}
      />

      {/* Test Results and Diagnostic Console */}
      <TestResultsPanel
        targetTestSpec={repair.target_test}
        testFile={repair.test_file}
        attempts={repair.attempts}
        currentAttempt={repair.current_attempt}
        status={repair.status}
        targetResult={{
          passed: latestAttempt?.target_passed,
          duration_ms: (latestAttempt?.latency_ms || 0) / 2,
          failure_type: latestAttempt?.failure_type,
        }}
        regressionResult={{
          passed: latestAttempt?.regression_passed,
          duration_ms: (latestAttempt?.latency_ms || 0) / 2,
        }}
      />

      {/* Attempt Progression Timeline */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold font-mono uppercase text-zinc-200 flex items-center gap-2">
          <Activity className="w-4 h-4 text-emerald-400" />
          Attempt History & Feedback Loop ({repair.attempts.length})
        </h3>
        <AttemptTimeline attempts={repair.attempts} />
      </div>

      {/* Real-time WebSocket Event Log */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4">
        <button
          onClick={() => setShowEvents(!showEvents)}
          className="flex items-center justify-between w-full text-xs font-mono text-zinc-400 hover:text-zinc-200"
        >
          <span className="flex items-center gap-2">
            <Terminal className="w-3.5 h-3.5 text-emerald-400" />
            LIVE TELEMETRY EVENT STREAM ({events.length} events recorded)
          </span>
          <span>{showEvents ? 'HIDE LOGS' : 'VIEW LOGS'}</span>
        </button>

        {showEvents && (
          <div className="mt-3 space-y-1 max-h-48 overflow-y-auto font-mono text-[11px] bg-zinc-950 p-3 rounded border border-zinc-800">
            {events.map((e, idx) => (
              <div key={idx} className="text-zinc-400 flex items-start gap-2">
                <span className="text-zinc-600 select-none">[{new Date(e.timestamp).toLocaleTimeString()}]</span>
                <span className="text-emerald-400 font-semibold">{e.event_type}</span>
                <span className="text-zinc-500 truncate">{JSON.stringify(e.payload)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
