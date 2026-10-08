import React, { useState } from 'react';
import { CheckCircle2, XCircle, Clock, ChevronDown, ChevronRight, Terminal } from 'lucide-react';

interface TestResultsPanelProps {
  targetResult?: {
    passed?: boolean;
    duration_ms?: number;
    failure_type?: string;
    stdout?: string;
    stderr?: string;
  };
  regressionResult?: {
    passed?: boolean;
    total?: number;
    passed_tests?: number;
    failed_tests?: number;
    duration_ms?: number;
    stdout?: string;
    stderr?: string;
    failure_type?: string;
  };
}

export const TestResultsPanel: React.FC<TestResultsPanelProps> = ({
  targetResult,
  regressionResult,
}) => {
  const [expandTarget, setExpandTarget] = useState(false);
  const [expandRegression, setExpandRegression] = useState(false);

  const targetPassed = Boolean(targetResult?.passed);
  const regPassed = Boolean(regressionResult?.passed);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Target Test Card */}
      <div className={`p-4 rounded-lg border transition ${
        targetResult
          ? targetPassed
            ? 'bg-emerald-950/20 border-emerald-900/40'
            : 'bg-rose-950/20 border-rose-900/40'
          : 'bg-zinc-900/50 border-zinc-800'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {targetResult ? (
              targetPassed ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              ) : (
                <XCircle className="w-5 h-5 text-rose-400" />
              )
            ) : (
              <Clock className="w-5 h-5 text-zinc-400" />
            )}
            <div>
              <h4 className="text-xs font-mono uppercase text-zinc-400">Target Test Suite</h4>
              <p className="text-base font-bold font-mono text-zinc-100">
                {targetResult ? (targetPassed ? 'PASS' : 'FAIL') : 'QUEUED'}
              </p>
            </div>
          </div>

          <div className="text-right text-xs font-mono text-zinc-400">
            <div>Duration: {((targetResult?.duration_ms || 0) / 1000).toFixed(2)}s</div>
            {targetResult?.failure_type && targetResult.failure_type !== 'NONE' && (
              <span className="text-rose-400 font-semibold">{targetResult.failure_type}</span>
            )}
          </div>
        </div>

        {targetResult && (targetResult.stdout || targetResult.stderr) && (
          <div className="mt-3 pt-3 border-t border-zinc-800/80">
            <button
              onClick={() => setExpandTarget(!expandTarget)}
              className="flex items-center gap-1.5 text-xs font-mono text-zinc-400 hover:text-zinc-200 transition"
            >
              {expandTarget ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              <Terminal className="w-3.5 h-3.5 text-zinc-400" />
              <span>Sandbox pytest logs</span>
            </button>
            {expandTarget && (
              <pre className="mt-2 p-3 bg-zinc-950 text-zinc-300 font-mono text-[11px] rounded border border-zinc-800 overflow-x-auto max-h-48 whitespace-pre">
                {targetResult.stdout || targetResult.stderr}
              </pre>
            )}
          </div>
        )}
      </div>

      {/* Regression Suite Card */}
      <div className={`p-4 rounded-lg border transition ${
        regressionResult
          ? regPassed
            ? 'bg-emerald-950/20 border-emerald-900/40'
            : 'bg-rose-950/20 border-rose-900/40'
          : 'bg-zinc-900/50 border-zinc-800'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {regressionResult ? (
              regPassed ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              ) : (
                <XCircle className="w-5 h-5 text-rose-400" />
              )
            ) : (
              <Clock className="w-5 h-5 text-zinc-400" />
            )}
            <div>
              <h4 className="text-xs font-mono uppercase text-zinc-400">Regression Test Suite</h4>
              <p className="text-base font-bold font-mono text-zinc-100">
                {regressionResult
                  ? `${regressionResult.passed_tests || 0} passed${
                      (regressionResult.failed_tests || 0) > 0 ? `, ${regressionResult.failed_tests} failed` : ''
                    }`
                  : 'QUEUED'}
              </p>
            </div>
          </div>

          <div className="text-right text-xs font-mono text-zinc-400">
            <div>Duration: {((regressionResult?.duration_ms || 0) / 1000).toFixed(2)}s</div>
            {regressionResult && !regPassed && (
              <span className="text-rose-400 font-semibold">REGRESSION DETECTED</span>
            )}
          </div>
        </div>

        {regressionResult && (regressionResult.stdout || regressionResult.stderr) && (
          <div className="mt-3 pt-3 border-t border-zinc-800/80">
            <button
              onClick={() => setExpandRegression(!expandRegression)}
              className="flex items-center gap-1.5 text-xs font-mono text-zinc-400 hover:text-zinc-200 transition"
            >
              {expandRegression ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              <Terminal className="w-3.5 h-3.5 text-zinc-400" />
              <span>Regression pytest logs</span>
            </button>
            {expandRegression && (
              <pre className="mt-2 p-3 bg-zinc-950 text-zinc-300 font-mono text-[11px] rounded border border-zinc-800 overflow-x-auto max-h-48 whitespace-pre">
                {regressionResult.stdout || regressionResult.stderr}
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
