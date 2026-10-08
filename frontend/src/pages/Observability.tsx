import React from 'react';
import { ExternalLink, ShieldCheck, Terminal, Cpu, Database, Activity, CheckCircle2 } from 'lucide-react';

export const Observability: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="pb-6 border-b border-zinc-800">
        <h1 className="text-2xl font-bold tracking-tight text-zinc-100 flex items-center gap-2.5">
          Observability & Tracing Architecture
        </h1>
        <p className="text-sm text-zinc-400 mt-1 max-w-3xl">
          Complete nested observability with Langfuse telemetry, structured span tracking, token accounting, and sandboxed execution metrics.
        </p>
      </div>

      {/* Integration Card */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-zinc-100">Langfuse Tracing Engine</h2>
              <p className="text-xs text-zinc-400 font-mono">
                Environment: Configured with graceful degradation when credentials are unset
              </p>
            </div>
          </div>

          <a
            href="https://cloud.langfuse.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-md bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-xs font-mono font-semibold text-zinc-200 transition"
          >
            <span>OPEN LANGFUSE CLOUD</span>
            <ExternalLink className="w-4 h-4 text-emerald-400" />
          </a>
        </div>

        {/* Trace Structure Breakdown */}
        <div className="space-y-3 font-mono text-xs">
          <span className="text-zinc-400 uppercase text-[11px] block">
            Hierarchical Span Pipeline Anatomy:
          </span>
          <div className="bg-zinc-950 p-4 rounded-md border border-zinc-800 space-y-2 text-zinc-300">
            <div className="text-emerald-400 font-bold">
              • trace_repair_ABC123 <span className="text-zinc-500">(Parent Workflow Trace)</span>
            </div>
            <div className="pl-4 text-zinc-400">├── initialize_repair <span className="text-zinc-600">[span]</span></div>
            <div className="pl-4 text-zinc-400">├── inspect_workspace <span className="text-zinc-600">[span]</span></div>
            <div className="pl-4 text-zinc-400">├── analyze_failure <span className="text-zinc-600">[span]</span></div>
            <div className="pl-4 text-indigo-400">
              ├── coder_attempt_1 <span className="text-zinc-500">[generation: openai/gpt-oss-120b]</span>
            </div>
            <div className="pl-8 text-zinc-400">├── tool_read_file <span className="text-zinc-600">[tool_call]</span></div>
            <div className="pl-8 text-zinc-400">├── tool_apply_patch <span className="text-zinc-600">[tool_call]</span></div>
            <div className="pl-4 text-zinc-400">├── target_test <span className="text-emerald-400">[sandbox pytest: PASS]</span></div>
            <div className="pl-4 text-zinc-400">├── regression_suite <span className="text-rose-400">[sandbox pytest: FAIL]</span></div>
            <div className="pl-4 text-purple-400">
              ├── critic_attempt_1 <span className="text-zinc-500">[generation: openai/gpt-oss-20b: REVISE]</span>
            </div>
            <div className="pl-4 text-indigo-400">
              ├── coder_attempt_2 <span className="text-zinc-500">[generation: revised patch]</span>
            </div>
            <div className="pl-8 text-zinc-400">├── tool_apply_patch <span className="text-zinc-600">[tool_call]</span></div>
            <div className="pl-4 text-zinc-400">├── target_test <span className="text-emerald-400">[sandbox pytest: PASS]</span></div>
            <div className="pl-4 text-zinc-400">├── regression_suite <span className="text-emerald-400">[sandbox pytest: PASS]</span></div>
            <div className="pl-4 text-purple-400">
              ├── critic_attempt_2 <span className="text-zinc-500">[generation: PASS]</span>
            </div>
            <div className="pl-4 text-emerald-400 font-bold">└── finalize_success <span className="text-zinc-500">[end]</span></div>
          </div>
        </div>

        {/* Security & Observability Guarantees */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-zinc-800 text-xs font-mono">
          <div className="p-3 bg-zinc-950/60 rounded border border-zinc-800/80">
            <span className="text-emerald-400 block font-semibold mb-1 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" /> Secret Masking
            </span>
            <p className="text-zinc-400 text-[11px]">
              API keys and host secrets are never logged in spans or sent to third-party collectors.
            </p>
          </div>

          <div className="p-3 bg-zinc-950/60 rounded border border-zinc-800/80">
            <span className="text-emerald-400 block font-semibold mb-1 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" /> Non-Blocking Tracing
            </span>
            <p className="text-zinc-400 text-[11px]">
              Observability network blips will never crash or interrupt the autonomous repair graph.
            </p>
          </div>

          <div className="p-3 bg-zinc-950/60 rounded border border-zinc-800/80">
            <span className="text-emerald-400 block font-semibold mb-1 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" /> Token Accounting
            </span>
            <p className="text-zinc-400 text-[11px]">
              Prompt tokens and completion tokens are tracked per attempt across Coder and Critic models.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
