import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Cpu, Activity, PlayCircle, BarChart3, ShieldCheck, Terminal } from 'lucide-react';

export const Navbar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { label: 'Dashboard', path: '/', icon: Activity },
    { label: 'New Repair', path: '/new', icon: PlayCircle },
    { label: 'Benchmarks', path: '/benchmarks', icon: BarChart3 },
    { label: 'Observability', path: '/observability', icon: ShieldCheck },
  ];

  return (
    <header className="sticky top-0 z-50 bg-zinc-950/80 backdrop-blur border-b border-zinc-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-500/20 transition">
              <Cpu className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <span className="font-bold text-zinc-100 tracking-tight text-base block leading-none">
                Self-Healing <span className="text-emerald-400 font-mono text-xs px-1.5 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/40 ml-1">PIPELINE</span>
              </span>
              <span className="text-xs text-zinc-400 font-mono">Autonomous Code Repair</span>
            </div>
          </Link>
        </div>

        <nav className="flex items-center gap-1 sm:gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition ${
                  isActive
                    ? 'bg-zinc-800 text-zinc-100 border border-zinc-700'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono bg-zinc-900 border border-zinc-800 text-zinc-400">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            <span>SANDBOX: DOCKER / ISOLATED</span>
          </div>
          <Link
            to="/new"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-sm"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>START RUN</span>
          </Link>
        </div>
      </div>
    </header>
  );
};
