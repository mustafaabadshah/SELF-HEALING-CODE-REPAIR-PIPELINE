import React, { useState, useMemo } from 'react';
import {
  CheckCircle2,
  XCircle,
  Clock,
  Terminal,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  AlertTriangle,
  Layers,
  Sparkles,
  FileCode2,
} from 'lucide-react';
import { AttemptSummary, TestRunSummary } from '../types';

interface TestResultsPanelProps {
  targetTestSpec?: string;
  testFile?: string;
  attempts?: AttemptSummary[];
  currentAttempt?: number;
  status?: string;
  targetResult?: {
    passed?: boolean;
    duration_ms?: number;
    failure_type?: string;
    stdout?: string;
    stderr?: string;
    exit_code?: number;
  };
  regressionResult?: {
    passed?: boolean;
    total?: number;
    passed_tests?: number;
    failed_tests?: number;
    failed_names?: string[];
    duration_ms?: number;
    stdout?: string;
    stderr?: string;
    failure_type?: string;
    exit_code?: number;
  };
}

export const TestResultsPanel: React.FC<TestResultsPanelProps> = ({
  targetTestSpec,
  testFile,
  attempts = [],
  currentAttempt,
  status,
  targetResult: propTargetResult,
  regressionResult: propRegressionResult,
}) => {
  // Attempt selector state
  const attemptCount = attempts.length;
  const [selectedAttemptIndex, setSelectedAttemptIndex] = useState<number>(
    attemptCount > 0 ? attemptCount - 1 : 0
  );
  const [activeConsoleTab, setActiveConsoleTab] = useState<'target' | 'regression' | 'all'>('target');
  const [copied, setCopied] = useState(false);
  const [isConsoleExpanded, setIsConsoleExpanded] = useState(true);

  // Sync with new attempts as they arrive
  React.useEffect(() => {
    if (attemptCount > 0) {
      setSelectedAttemptIndex(attemptCount - 1);
    }
  }, [attemptCount]);

  const currentAttemptRecord: AttemptSummary | undefined = attempts[selectedAttemptIndex];

  // Resolve target & regression test run data for currently selected attempt
  const targetRun: Partial<TestRunSummary> | undefined = useMemo(() => {
    if (currentAttemptRecord?.test_runs && currentAttemptRecord.test_runs.length > 0) {
      const found = currentAttemptRecord.test_runs.find((r) => r.type === 'TARGET');
      if (found) return found;
    }
    if (currentAttemptRecord) {
      return {
        passed: currentAttemptRecord.target_passed,
        duration_ms: (currentAttemptRecord.latency_ms || 0) / 2,
        failure_type: currentAttemptRecord.failure_type,
        exit_code: currentAttemptRecord.target_passed ? 0 : 1,
        stdout: '',
        stderr: '',
      };
    }
    return propTargetResult;
  }, [currentAttemptRecord, propTargetResult]);

  const regressionRun: Partial<TestRunSummary> & {
    total?: number;
    passed_tests?: number;
    failed_tests?: number;
    failed_names?: string[];
  } | undefined = useMemo(() => {
    if (currentAttemptRecord?.test_runs && currentAttemptRecord.test_runs.length > 0) {
      const found = currentAttemptRecord.test_runs.find((r) => r.type === 'REGRESSION');
      if (found) return found;
    }
    if (currentAttemptRecord) {
      const passed = currentAttemptRecord.regression_passed;
      return {
        passed,
        duration_ms: (currentAttemptRecord.latency_ms || 0) / 2,
        failure_type: passed ? 'NONE' : 'REGRESSION',
        exit_code: passed ? 0 : 1,
        total: 2,
        passed_tests: passed ? 2 : 0,
        failed_tests: passed ? 0 : 1,
        stdout: '',
        stderr: '',
      };
    }
    return propRegressionResult;
  }, [currentAttemptRecord, propRegressionResult]);

  const targetPassed = Boolean(targetRun?.passed);
  const regPassed = Boolean(regressionRun?.passed);

  // Pytest console content
  const targetStdout = targetRun?.stdout || '';
  const targetStderr = targetRun?.stderr || '';
  const regStdout = regressionRun?.stdout || '';
  const regStderr = regressionRun?.stderr || '';

  const activeOutput = useMemo(() => {
    if (activeConsoleTab === 'target') {
      return targetStdout || targetStderr || '(No raw logs recorded for target test run)';
    } else if (activeConsoleTab === 'regression') {
      return regStdout || regStderr || '(No raw logs recorded for regression test run)';
    } else {
      const parts = [];
      if (targetStdout || targetStderr) {
        parts.push(`=== TARGET TEST RUN (${targetTestSpec || 'Target'}) ===\n${targetStdout}\n${targetStderr}`);
      }
      if (regStdout || regStderr) {
        parts.push(`=== REGRESSION SUITE RUN ===\n${regStdout}\n${regStderr}`);
      }
      return parts.length > 0 ? parts.join('\n\n') : '(No sandbox pytest logs captured)';
    }
  }, [activeConsoleTab, targetStdout, targetStderr, regStdout, regStderr, targetTestSpec]);

  const handleCopyLogs = () => {
    navigator.clipboard.writeText(activeOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Determine latest test status badge and description
  const isExecuting = status === 'RUNNING' || status === 'SELF_CORRECTING';
  const effectiveAttemptNum = currentAttemptRecord ? currentAttemptRecord.attempt_number : currentAttempt || 1;

  return (
    <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl overflow-hidden shadow-sm space-y-0">
      {/* 1. Header & Attempt Selector */}
      <div className="p-4 sm:p-5 border-b border-zinc-800/80 bg-zinc-900/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <FileCode2 className="w-4 h-4" />
            </span>
            <h3 className="text-sm font-bold text-zinc-100 font-mono tracking-wide uppercase">
              Sandbox Test Execution & Diagnostics
            </h3>
          </div>
          <p className="text-xs text-zinc-400 mt-1 font-mono">
            Latest executed test spec:{' '}
            <span className="text-zinc-200 font-bold bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800">
              {targetTestSpec || testFile || 'pytest target suite'}
            </span>
          </p>
        </div>

        {/* Attempt tabs switcher */}
        {attemptCount > 0 && (
          <div className="flex items-center gap-1.5 bg-zinc-950/80 p-1 rounded-lg border border-zinc-800 overflow-x-auto">
            <span className="text-[11px] font-mono text-zinc-500 px-2 flex items-center gap-1">
              <Layers className="w-3 h-3" /> Attempts:
            </span>
            {attempts.map((att, idx) => {
              const isSelected = selectedAttemptIndex === idx;
              const isAttemptPass = att.target_passed && att.regression_passed;
              const isRegressionFail = att.target_passed && !att.regression_passed;
              return (
                <button
                  key={att.id || idx}
                  onClick={() => setSelectedAttemptIndex(idx)}
                  className={`px-2.5 py-1 rounded text-xs font-mono font-medium transition flex items-center gap-1.5 ${
                    isSelected
                      ? 'bg-zinc-800 text-zinc-100 border border-zinc-700 shadow-sm'
                      : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'
                  }`}
                >
                  <span>Attempt {att.attempt_number}</span>
                  {isAttemptPass ? (
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  ) : isRegressionFail ? (
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400" title="Regression caught" />
                  ) : (
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 2. Highlight Box: Plain-English Diagnostic of What the Last Test Did */}
      <div className="p-4 sm:p-5 border-b border-zinc-800/60 bg-zinc-950/40">
        <div className="flex items-start gap-3">
          {targetPassed && regPassed ? (
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 shrink-0 mt-0.5">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          ) : targetPassed && !regPassed ? (
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 shrink-0 mt-0.5">
              <AlertTriangle className="w-5 h-5" />
            </div>
          ) : (
            <div className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 shrink-0 mt-0.5">
              <XCircle className="w-5 h-5" />
            </div>
          )}

          <div className="space-y-1.5 flex-1">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <h4 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
                <span>Attempt {effectiveAttemptNum} Verification Verdict:</span>
                {targetPassed && regPassed ? (
                  <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">
                    100% ALL TESTS PASSED
                  </span>
                ) : targetPassed && !regPassed ? (
                  <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-amber-950 text-amber-300 border border-amber-800">
                    TARGET PASSED - REGRESSION DETECTED
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-rose-950 text-rose-300 border border-rose-800">
                    TARGET TEST FAILED
                  </span>
                )}
              </h4>
              <div className="flex items-center gap-2 text-xs font-mono text-zinc-400">
                <span>Exit Code: <strong className={targetPassed && regPassed ? 'text-emerald-400' : 'text-rose-400'}>{targetPassed && regPassed ? '0' : '1'}</strong></span>
                <span>•</span>
                <span>Total Time: <strong>{(((targetRun?.duration_ms || 0) + (regressionRun?.duration_ms || 0)) / 1000).toFixed(2)}s</strong></span>
              </div>
            </div>

            <p className="text-xs text-zinc-300 leading-relaxed">
              {targetPassed && regPassed ? (
                <>
                  <strong className="text-emerald-300">Clean repair verified!</strong> The isolated sandbox ran both the failing target test and the existing regression suites. All assertions returned true without breaking backwards compatibility.
                </>
              ) : targetPassed && !regPassed ? (
                <>
                  <strong className="text-amber-300">Regression caught by pipeline!</strong> The code modification passed the target test, but broke one or more existing regression tests. The self-healing loop automatically discarded this candidate and scheduled a revision.
                </>
              ) : (
                <>
                  <strong className="text-rose-300">Assertion or syntax failure.</strong> The code under test failed to satisfy the target specification. Check the pytest execution logs below to see the exact traceback and expected vs. actual values.
                </>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* 3. Side-by-Side Target Test Card & Regression Card */}
      <div className="p-4 sm:p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Target Test Card */}
        <div
          className={`p-4 rounded-xl border transition ${
            targetRun
              ? targetPassed
                ? 'bg-emerald-950/20 border-emerald-900/40'
                : 'bg-rose-950/20 border-rose-900/40'
              : 'bg-zinc-950/50 border-zinc-800'
          }`}
        >
          <div className="flex items-center justify-between pb-3 border-b border-zinc-800/80">
            <div className="flex items-center gap-2.5">
              {targetRun ? (
                targetPassed ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                ) : (
                  <XCircle className="w-5 h-5 text-rose-400 shrink-0" />
                )
              ) : (
                <Clock className="w-5 h-5 text-zinc-500 shrink-0 animate-pulse" />
              )}
              <div>
                <h4 className="text-xs font-mono uppercase tracking-wider text-zinc-400">Target Test Suite</h4>
                <div className="text-base font-bold font-mono text-zinc-100 flex items-center gap-2">
                  <span>{targetRun ? (targetPassed ? 'PASS' : 'FAIL') : isExecuting ? 'RUNNING...' : 'QUEUED'}</span>
                  {targetRun?.exit_code !== undefined && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                      exit {targetRun.exit_code}
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="text-right text-xs font-mono text-zinc-400 space-y-0.5">
              <div>Time: {((targetRun?.duration_ms || 0) / 1000).toFixed(2)}s</div>
              {targetRun?.failure_type && targetRun.failure_type !== 'NONE' && (
                <span className="text-rose-400 font-bold block text-[11px]">{targetRun.failure_type}</span>
              )}
            </div>
          </div>

          <div className="mt-3 text-xs font-mono text-zinc-400 space-y-1">
            <div className="flex items-center justify-between">
              <span>Spec:</span>
              <span className="text-zinc-300 truncate max-w-[220px]" title={targetTestSpec}>
                {targetTestSpec || 'test_target.py'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>Status:</span>
              <span className={targetPassed ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>
                {targetPassed ? 'Target criterion satisfied' : 'Target assertion failure'}
              </span>
            </div>
          </div>
        </div>

        {/* Regression Test Suite Card */}
        <div
          className={`p-4 rounded-xl border transition ${
            regressionRun
              ? regPassed
                ? 'bg-emerald-950/20 border-emerald-900/40'
                : 'bg-rose-950/20 border-rose-900/40'
              : 'bg-zinc-950/50 border-zinc-800'
          }`}
        >
          <div className="flex items-center justify-between pb-3 border-b border-zinc-800/80">
            <div className="flex items-center gap-2.5">
              {regressionRun ? (
                regPassed ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                ) : (
                  <XCircle className="w-5 h-5 text-rose-400 shrink-0" />
                )
              ) : (
                <Clock className="w-5 h-5 text-zinc-500 shrink-0" />
              )}
              <div>
                <h4 className="text-xs font-mono uppercase tracking-wider text-zinc-400">Regression Test Suite</h4>
                <div className="text-base font-bold font-mono text-zinc-100 flex items-center gap-2">
                  <span>{regressionRun ? (regPassed ? 'PASS' : 'REGRESSION') : isExecuting ? 'RUNNING...' : 'QUEUED'}</span>
                  {regressionRun?.exit_code !== undefined && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                      exit {regressionRun.exit_code}
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="text-right text-xs font-mono text-zinc-400 space-y-0.5">
              <div>Time: {((regressionRun?.duration_ms || 0) / 1000).toFixed(2)}s</div>
              {regressionRun && !regPassed && (
                <span className="text-rose-400 font-bold block text-[11px]">REGRESSION DETECTED</span>
              )}
            </div>
          </div>

          <div className="mt-3 text-xs font-mono text-zinc-400 space-y-1">
            <div className="flex items-center justify-between">
              <span>Tests Run:</span>
              <span className="text-zinc-300">
                {regressionRun
                  ? `${regressionRun.passed_tests ?? (regPassed ? 2 : 0)} passed${
                      (regressionRun.failed_tests || 0) > 0 ? `, ${regressionRun.failed_tests} failed` : ''
                    }`
                  : 'Pending execution'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>Integrity:</span>
              <span className={regPassed ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>
                {regPassed ? 'No regressions detected' : 'Existing functionality compromised'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Full Pytest Logs Terminal with Traceback Inspection */}
      <div className="p-4 sm:p-5 pt-0">
        <div className="bg-[#090d16] rounded-xl border border-zinc-800 overflow-hidden shadow-inner">
          {/* Terminal Title Bar */}
          <div className="px-4 py-2.5 bg-zinc-950 border-b border-zinc-800/80 flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsConsoleExpanded(!isConsoleExpanded)}
                className="flex items-center gap-1.5 text-xs font-mono text-zinc-300 hover:text-white transition"
              >
                {isConsoleExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                <span className="font-semibold">Sandbox Pytest Logs & Diagnostics</span>
              </button>

              {/* Log View Tabs */}
              {isConsoleExpanded && (
                <div className="flex items-center gap-1 bg-zinc-900 p-0.5 rounded border border-zinc-800 text-[11px] font-mono">
                  <button
                    onClick={() => setActiveConsoleTab('target')}
                    className={`px-2 py-0.5 rounded transition ${
                      activeConsoleTab === 'target'
                        ? 'bg-zinc-800 text-zinc-100 font-semibold'
                        : 'text-zinc-400 hover:text-zinc-200'
                    }`}
                  >
                    Target Log
                  </button>
                  <button
                    onClick={() => setActiveConsoleTab('regression')}
                    className={`px-2 py-0.5 rounded transition ${
                      activeConsoleTab === 'regression'
                        ? 'bg-zinc-800 text-zinc-100 font-semibold'
                        : 'text-zinc-400 hover:text-zinc-200'
                    }`}
                  >
                    Regression Log
                  </button>
                  <button
                    onClick={() => setActiveConsoleTab('all')}
                    className={`px-2 py-0.5 rounded transition ${
                      activeConsoleTab === 'all'
                        ? 'bg-zinc-800 text-zinc-100 font-semibold'
                        : 'text-zinc-400 hover:text-zinc-200'
                    }`}
                  >
                    All Logs
                  </button>
                </div>
              )}
            </div>

            {isConsoleExpanded && (
              <button
                onClick={handleCopyLogs}
                className="flex items-center gap-1 text-[11px] font-mono text-zinc-400 hover:text-zinc-200 bg-zinc-900 hover:bg-zinc-800 px-2 py-1 rounded border border-zinc-800 transition"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Copied' : 'Copy Logs'}</span>
              </button>
            )}
          </div>

          {/* Terminal Body */}
          {isConsoleExpanded && (
            <div className="p-4 overflow-x-auto max-h-72 font-mono text-[11.5px] leading-relaxed text-zinc-300 whitespace-pre">
              {activeOutput.split('\n').map((line, idx) => {
                let lineClass = 'text-zinc-300';
                if (line.includes('PASSED')) lineClass = 'text-emerald-400 font-semibold';
                else if (line.includes('FAILED') || line.includes('AssertionError') || line.startsWith('E   '))
                  lineClass = 'text-rose-400 font-semibold bg-rose-950/30 px-1 rounded';
                else if (line.startsWith('>') || line.includes('assert '))
                  lineClass = 'text-amber-300 font-semibold';
                else if (line.startsWith('===') || line.startsWith('platform '))
                  lineClass = 'text-zinc-500';

                return (
                  <div key={idx} className={lineClass}>
                    {line || ' '}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
