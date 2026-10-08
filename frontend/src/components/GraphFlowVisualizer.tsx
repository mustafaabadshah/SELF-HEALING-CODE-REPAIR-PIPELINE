import React from 'react';
import {
  FileSearch,
  Bot,
  Wrench,
  CheckCircle2,
  XCircle,
  ShieldAlert,
  GitCompare,
  ArrowRight,
  RotateCcw,
} from 'lucide-react';

interface GraphFlowVisualizerProps {
  activeNode: string;
  attempt: number;
  maxAttempts: number;
  status: string;
}

export const GraphFlowVisualizer: React.FC<GraphFlowVisualizerProps> = ({
  activeNode,
  attempt,
  maxAttempts,
  status,
}) => {
  const steps = [
    { id: 'inspect_workspace', label: 'Inspect', icon: FileSearch },
    { id: 'analyze_failure', label: 'Analyze', icon: ShieldAlert },
    { id: 'coder', label: 'Coder Agent', icon: Bot },
    { id: 'execute_tools', label: 'Tools / Patch', icon: Wrench },
    { id: 'target_test', label: 'Target Test', icon: CheckCircle2 },
    { id: 'regression_test', label: 'Regression Suite', icon: GitCompare },
    { id: 'critic', label: 'Critic Agent', icon: Bot },
    { id: 'route_decision', label: 'Router Decision', icon: RotateCcw },
  ];

  const getNodeState = (nodeId: string) => {
    if (status === 'SUCCESS') return 'completed';
    if (status === 'FAILED') return 'failed';
    if (activeNode === nodeId) return 'active';
    return 'idle';
  };

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4 overflow-x-auto">
      <div className="flex items-center justify-between mb-3 text-xs font-mono text-zinc-400">
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          LANGGRAPH STATEGRAPH WORKFLOW
        </span>
        <span className="px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-300">
          ATTEMPT {attempt} / {maxAttempts}
        </span>
      </div>

      <div className="flex items-center gap-2 min-w-[760px] justify-between py-2">
        {steps.map((s, idx) => {
          const Icon = s.icon;
          const nodeState = getNodeState(s.id);
          const isActive = nodeState === 'active';
          const isCompleted = nodeState === 'completed';

          return (
            <React.Fragment key={s.id}>
              <div
                className={`flex flex-col items-center gap-1.5 p-2 rounded-lg border transition-all text-center min-w-[85px] ${
                  isActive
                    ? 'border-emerald-500 bg-emerald-950/40 text-emerald-300 shadow-md shadow-emerald-950 ring-1 ring-emerald-500/50'
                    : isCompleted
                    ? 'border-zinc-700 bg-zinc-900/90 text-zinc-300'
                    : 'border-zinc-800/80 bg-zinc-950/60 text-zinc-400'
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-md flex items-center justify-center ${
                    isActive
                      ? 'bg-emerald-500 text-zinc-950'
                      : isCompleted
                      ? 'bg-zinc-800 text-emerald-400'
                      : 'bg-zinc-900 text-zinc-400'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'animate-bounce' : ''}`} />
                </div>
                <span className="text-[11px] font-mono leading-tight">{s.label}</span>
              </div>

              {idx < steps.length - 1 && (
                <ArrowRight className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
