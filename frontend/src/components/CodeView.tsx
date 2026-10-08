import React, { useState } from 'react';
import { FileCode, Plus, Minus, Copy, Check } from 'lucide-react';

interface CodeViewProps {
  originalCode: string;
  currentCode: string;
  diff: string;
  filename: string;
}

export const CodeView: React.FC<CodeViewProps> = ({
  originalCode,
  currentCode,
  diff,
  filename,
}) => {
  const [activeTab, setActiveTab] = useState<'diff' | 'current' | 'original'>('diff');
  const [copied, setCopied] = useState(false);

  const diffLines = (diff || '').split('\n');
  const linesAdded = diffLines.filter((l) => l.startsWith('+') && !l.startsWith('+++')).length;
  const linesRemoved = diffLines.filter((l) => l.startsWith('-') && !l.startsWith('---')).length;

  const handleCopy = () => {
    const textToCopy =
      activeTab === 'diff' ? diff : activeTab === 'current' ? currentCode : originalCode;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg overflow-hidden">
      {/* Top Header */}
      <div className="px-4 py-3 bg-zinc-950/80 border-b border-zinc-800 flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs font-mono text-zinc-300">
            <FileCode className="w-4 h-4 text-emerald-400" />
            <span>{filename || 'module.py'}</span>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/40">
              <Plus className="w-3 h-3" /> {linesAdded} lines
            </span>
            <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded bg-rose-950/80 text-rose-400 border border-rose-800/40">
              <Minus className="w-3 h-3" /> {linesRemoved} lines
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Tabs */}
          <div className="flex items-center bg-zinc-900 p-0.5 rounded-md border border-zinc-800 text-xs font-mono">
            <button
              onClick={() => setActiveTab('diff')}
              className={`px-3 py-1 rounded transition ${
                activeTab === 'diff'
                  ? 'bg-zinc-800 text-zinc-100 font-semibold shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Unified Diff
            </button>
            <button
              onClick={() => setActiveTab('current')}
              className={`px-3 py-1 rounded transition ${
                activeTab === 'current'
                  ? 'bg-zinc-800 text-zinc-100 font-semibold shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Current Patched
            </button>
            <button
              onClick={() => setActiveTab('original')}
              className={`px-3 py-1 rounded transition ${
                activeTab === 'original'
                  ? 'bg-zinc-800 text-zinc-100 font-semibold shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Original
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="p-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 transition"
            title="Copy Code"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Code Body */}
      <div className="p-4 font-mono text-xs overflow-x-auto max-h-[420px] bg-zinc-950/90">
        {activeTab === 'diff' ? (
          diff ? (
            <div className="space-y-0.5">
              {diffLines.map((line, idx) => {
                let lineClass = 'text-zinc-400';
                if (line.startsWith('+++') || line.startsWith('---')) {
                  lineClass = 'text-zinc-500 font-bold';
                } else if (line.startsWith('@@')) {
                  lineClass = 'text-indigo-400 bg-indigo-950/20 py-0.5 block';
                } else if (line.startsWith('+')) {
                  lineClass = 'text-emerald-300 bg-emerald-950/40 block';
                } else if (line.startsWith('-')) {
                  lineClass = 'text-rose-300 bg-rose-950/40 block';
                }
                return (
                  <div key={idx} className={`px-2 font-mono whitespace-pre ${lineClass}`}>
                    {line}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-zinc-400 italic py-6 text-center">
              No patch modifications applied yet in current attempt.
            </div>
          )
        ) : activeTab === 'current' ? (
          <pre className="text-zinc-200 whitespace-pre">{currentCode || originalCode}</pre>
        ) : (
          <pre className="text-zinc-200 whitespace-pre">{originalCode}</pre>
        )}
      </div>
    </div>
  );
};
