import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string | number;
  sublabel?: string;
  icon: LucideIcon;
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  sublabel,
  icon: Icon,
  variant = 'default',
}) => {
  const variantStyles = {
    default: 'text-zinc-100 border-zinc-800 bg-zinc-900/50',
    success: 'text-emerald-400 border-emerald-900/40 bg-emerald-950/20',
    warning: 'text-amber-400 border-amber-900/40 bg-amber-950/20',
    danger: 'text-rose-400 border-rose-900/40 bg-rose-950/20',
  }[variant];

  return (
    <div className={`p-4 rounded-lg border flex items-center justify-between ${variantStyles}`}>
      <div>
        <p className="text-xs font-mono uppercase text-zinc-400">{label}</p>
        <p className="text-2xl font-bold font-mono tracking-tight mt-1">{value}</p>
        {sublabel && <p className="text-xs text-zinc-400 mt-1">{sublabel}</p>}
      </div>
      <div className="w-10 h-10 rounded-md bg-zinc-800/80 border border-zinc-700/50 flex items-center justify-center text-zinc-300">
        <Icon className="w-5 h-5" />
      </div>
    </div>
  );
};
