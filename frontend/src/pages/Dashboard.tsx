import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Coins,
  Cpu,
  PlusCircle,
  ArrowRight,
  RefreshCw,
  Terminal,
} from 'lucide-react';
import { getMetrics, listRepairs } from '../api/client';
import { DashboardMetrics, RepairDetail } from '../types';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';

export const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [repairs, setRepairs] = useState<RepairDetail[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [m, r] = await Promise.all([getMetrics(), listRepairs(20)]);
      setMetrics(m);
      setRepairs(r);
    } catch (e) {
      console.error('Failed to load dashboard:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Hero / Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-zinc-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-zinc-100 flex items-center gap-2.5">
            Self-Healing Code Repair Pipeline
          </h1>
          <p className="text-sm text-zinc-400 mt-1 max-w-2xl">
            Autonomous multi-agent code diagnosis, native tool function-calling, sandboxed test execution, regression detection, and deterministic self-critique.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            className="p-2 rounded-md bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 transition"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <Link
            to="/new"
            className="flex items-center gap-2 px-4 py-2 rounded-md bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition shadow-sm"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Repair Run</span>
          </Link>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Total Repair Runs"
          value={metrics?.total_repairs ?? 0}
          icon={Terminal}
          sublabel="All orchestrated runs"
        />
        <MetricCard
          label="Successful Repairs"
          value={metrics?.successful_repairs ?? 0}
          icon={CheckCircle2}
          variant="success"
          sublabel={
            metrics?.total_repairs
              ? `${Math.round((metrics.successful_repairs / metrics.total_repairs) * 100)}% success rate`
              : '0% success rate'
          }
        />
        <MetricCard
          label="Regression Rate"
          value={`${metrics?.regression_rate ?? 0}%`}
          icon={AlertTriangle}
          variant="warning"
          sublabel="Regressions caught by Critic"
        />
        <MetricCard
          label="Human Escalations"
          value={metrics?.escalations ?? 0}
          icon={Cpu}
          variant={metrics?.escalations ? 'danger' : 'default'}
          sublabel="Exceeded max attempts limit"
        />
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          label="Average Attempts"
          value={metrics?.average_attempts ?? 0}
          icon={RefreshCw}
          sublabel="Avg tries before solution"
        />
        <MetricCard
          label="Total LLM Tokens"
          value={(metrics?.total_tokens ?? 0).toLocaleString()}
          icon={Coins}
          sublabel="Coder + Critic calls"
        />
        <MetricCard
          label="Average Latency"
          value={`${((metrics?.average_latency_ms ?? 0) / 1000).toFixed(1)}s`}
          icon={Clock}
          sublabel="Per attempt roundtrip"
        />
      </div>

      {/* Recent Repairs Table */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg overflow-hidden">
        <div className="px-6 py-4 bg-zinc-950/80 border-b border-zinc-800 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-zinc-100 font-mono uppercase">
            Recent Repair Runs
          </h2>
          <span className="text-xs text-zinc-400 font-mono">
            Showing latest {repairs.length} records
          </span>
        </div>

        {repairs.length === 0 ? (
          <div className="p-12 text-center text-zinc-400 font-mono text-sm">
            <Terminal className="w-8 h-8 mx-auto text-zinc-600 mb-2" />
            <p>No repair runs recorded yet in the database.</p>
            <Link
              to="/new"
              className="inline-block mt-3 px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition"
            >
              Start Built-in Demo Repair
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs font-mono">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-950/40 text-zinc-400">
                  <th className="py-3 px-6 font-semibold">REPAIR ID</th>
                  <th className="py-3 px-6 font-semibold">STATUS</th>
                  <th className="py-3 px-6 font-semibold">ATTEMPTS</th>
                  <th className="py-3 px-6 font-semibold">SOURCE FILE</th>
                  <th className="py-3 px-6 font-semibold">TARGET TEST</th>
                  <th className="py-3 px-6 font-semibold">CREATED</th>
                  <th className="py-3 px-6 text-right font-semibold">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60 text-zinc-300">
                {repairs.map((r) => (
                  <tr key={r.id} className="hover:bg-zinc-900/40 transition">
                    <td className="py-3 px-6 font-bold text-zinc-200">
                      {r.id}
                    </td>
                    <td className="py-3 px-6">
                      <StatusBadge status={r.status} size="sm" />
                    </td>
                    <td className="py-3 px-6">
                      <span className="px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-300">
                        {r.current_attempt} / {r.max_attempts}
                      </span>
                    </td>
                    <td className="py-3 px-6 text-zinc-300">{r.source_file}</td>
                    <td className="py-3 px-6 text-zinc-400 truncate max-w-xs">{r.target_test}</td>
                    <td className="py-3 px-6 text-zinc-400">
                      {new Date(r.created_at).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-6 text-right">
                      <Link
                        to={`/repairs/${r.id}`}
                        className="inline-flex items-center gap-1 text-emerald-400 hover:text-emerald-300 font-semibold"
                      >
                        Inspect <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
