import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Folder,
  FolderSearch,
  UploadCloud,
  Code2,
  CheckCircle2,
  HelpCircle,
  PlayCircle,
  FileCode,
  ShieldCheck,
  Trash2,
  Plus,
  RefreshCw,
  AlertCircle,
  Terminal,
} from 'lucide-react';
import { createRepair, fetchPresets, scanDirectory } from '../api/client';
import { CreateRepairPayload, PresetItem, ScanDirectoryResponse } from '../types';

export const NewRepair: React.FC = () => {
  const navigate = useNavigate();

  // Active configuration mode
  const [activeTab, setActiveTab] = useState<'presets' | 'directory' | 'upload' | 'editor'>('presets');

  // Form State
  const [sourceFile, setSourceFile] = useState('buggy_module.py');
  const [sourceContent, setSourceContent] = useState('');
  const [testFile, setTestFile] = useState('test_target.py');
  const [testContent, setTestContent] = useState('');
  const [targetTest, setTargetTest] = useState('test_target.py::test_discount_with_percentage_string');
  const [regressionTests, setRegressionTests] = useState<{ filename: string; content: string }[]>([]);
  const [maxAttempts, setMaxAttempts] = useState(3);
  const [useMock, setUseMock] = useState(false);

  // Directory Scan State
  const [dirPathInput, setDirPathInput] = useState('examples/regression_demo');
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<ScanDirectoryResponse | null>(null);
  const [scanError, setScanError] = useState<string | null>(null);

  // Presets State
  const [presets, setPresets] = useState<PresetItem[]>([]);
  const [selectedPresetId, setSelectedPresetId] = useState<string>('ecommerce_discount');

  // Global submit state
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLaymanGuide, setShowLaymanGuide] = useState(true);

  // Load presets on mount
  useEffect(() => {
    async function loadPresetsList() {
      try {
        const data = await fetchPresets();
        setPresets(data);
        if (data.length > 0) {
          applyPreset(data[0]);
        }
      } catch (err: any) {
        console.error('Failed to load presets:', err);
      }
    }
    loadPresetsList();
  }, []);

  const applyPreset = (preset: PresetItem) => {
    setSelectedPresetId(preset.id);
    setSourceFile(preset.source_file);
    setSourceContent(preset.source_content);
    setTestFile(preset.test_file);
    setTestContent(preset.test_content);
    setTargetTest(preset.target_test);
    setRegressionTests(preset.regression_tests || []);
    setMaxAttempts(preset.max_attempts || 3);
    setError(null);
  };

  const handleScanDirectory = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!dirPathInput.trim()) return;

    try {
      setScanning(true);
      setScanError(null);
      const res = await scanDirectory(dirPathInput.trim());
      setScanResult(res);

      // Auto-populate form if files found
      if (res.source_files.length > 0) {
        const primarySource = res.source_files[0];
        setSourceFile(primarySource.filename);
        setSourceContent(primarySource.content);
      }

      if (res.test_files.length > 0) {
        const targetTgt = res.test_files.find((f) => f.filename.includes('target')) || res.test_files[0];
        setTestFile(targetTgt.filename);
        setTestContent(targetTgt.content);

        const firstTest = targetTgt.test_cases[0] || 'test_main';
        setTargetTest(`${targetTgt.filename}::${firstTest}`);

        // Set remaining as regression tests
        const regressions = res.test_files
          .filter((f) => f.filename !== targetTgt.filename)
          .map((f) => ({ filename: f.filename, content: f.content }));
        setRegressionTests(regressions);
      }
    } catch (err: any) {
      setScanError(err.message || 'Failed to scan directory');
    } finally {
      setScanning(false);
    }
  };

  // File Upload Handlers (Client-Side FileReader)
  const handleFileUpload = (
    e: React.ChangeEvent<HTMLInputElement>,
    type: 'source' | 'target_test' | 'regression'
  ) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    if (type === 'source') {
      const file = files[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        setSourceFile(file.name);
        setSourceContent(event.target?.result as string);
      };
      reader.readAsText(file);
    } else if (type === 'target_test') {
      const file = files[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        setTestFile(file.name);
        setTestContent(content);

        // Auto-extract first test function if possible
        const match = content.match(/def (test_\w+)\s*\(/);
        if (match) {
          setTargetTest(`${file.name}::${match[1]}`);
        } else {
          setTargetTest(`${file.name}::test_example`);
        }
      };
      reader.readAsText(file);
    } else if (type === 'regression') {
      Array.from(files).forEach((file) => {
        const reader = new FileReader();
        reader.onload = (event) => {
          setRegressionTests((prev) => [
            ...prev,
            { filename: file.name, content: event.target?.result as string },
          ]);
        };
        reader.readAsText(file);
      });
    }
  };

  const handleAddRegressionFile = () => {
    setRegressionTests((prev) => [
      ...prev,
      { filename: `test_regression_${prev.length + 1}.py`, content: '' },
    ]);
  };

  const handleRemoveRegressionFile = (index: number) => {
    setRegressionTests((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sourceContent.trim() || !testContent.trim()) {
      setError('Both source code and target test code are required to start the repair job.');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      const payload: CreateRepairPayload = {
        source_file: sourceFile,
        source_content: sourceContent,
        test_file: testFile,
        test_content: testContent,
        target_test: targetTest,
        regression_tests: regressionTests,
        max_attempts: maxAttempts,
        use_mock: useMock,
      };

      const res = await createRepair(payload);
      navigate(`/repairs/${res.repair_id}`);
    } catch (e: any) {
      setError(e.message);
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Page Header */}
      <div className="border-b border-zinc-800 pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/70 text-emerald-400 border border-emerald-800/60">
              Autonomous Code Repair
            </span>
            <span className="text-zinc-500">•</span>
            <span className="text-xs text-zinc-400 font-mono">Docker Sandbox Verified</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-zinc-100 mt-2">
            Start a New Self-Healing Repair
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Provide your broken code and test suites. The AI will autonomously diagnose, repair, and verify solutions in a sandbox.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowLaymanGuide(!showLaymanGuide)}
          className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 text-xs transition self-start md:self-center font-medium shadow-sm"
        >
          <HelpCircle className="w-4 h-4 text-emerald-400" />
          <span>{showLaymanGuide ? 'Hide Layman Guide' : 'How It Works (Layman Guide)'}</span>
        </button>
      </div>

      {/* Layman Friendly Step-by-Step Guide */}
      {showLaymanGuide && (
        <div className="bg-gradient-to-r from-emerald-950/30 via-zinc-900 to-indigo-950/30 border border-emerald-800/40 rounded-xl p-5 shadow-lg space-y-4">
          <div className="flex items-center gap-2 text-emerald-300 font-semibold text-sm">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span>How This System Works (In Plain English)</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="bg-zinc-950/60 p-3.5 rounded-lg border border-zinc-800/80 space-y-1.5">
              <div className="flex items-center gap-2 font-bold text-zinc-200">
                <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-mono text-xs">
                  1
                </span>
                <span>The Coder AI Analyzes</span>
              </div>
              <p className="text-zinc-400 leading-relaxed">
                The AI inspects your broken code, runs the failing test to reproduce the exact error, and writes a minimal surgical patch.
              </p>
            </div>

            <div className="bg-zinc-950/60 p-3.5 rounded-lg border border-zinc-800/80 space-y-1.5">
              <div className="flex items-center gap-2 font-bold text-zinc-200">
                <span className="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center font-mono text-xs">
                  2
                </span>
                <span>Sandbox Test & Regression Check</span>
              </div>
              <p className="text-zinc-400 leading-relaxed">
                The patch runs in an isolated container. It checks if the target bug is fixed <strong className="text-zinc-300">AND</strong> ensures no other existing features were accidentally broken.
              </p>
            </div>

            <div className="bg-zinc-950/60 p-3.5 rounded-lg border border-zinc-800/80 space-y-1.5">
              <div className="flex items-center gap-2 font-bold text-zinc-200">
                <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-mono text-xs">
                  3
                </span>
                <span>Critic Review & Self-Correction</span>
              </div>
              <p className="text-zinc-400 leading-relaxed">
                An impartial Critic AI reviews the results. If a fix introduced regressions, the bad code is rolled back and the Coder is instructed to revise its approach!
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Mode Switcher Tabs */}
      <div className="bg-zinc-900/80 p-1.5 rounded-xl border border-zinc-800 grid grid-cols-2 md:grid-cols-4 gap-1">
        <button
          type="button"
          onClick={() => setActiveTab('presets')}
          className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg text-xs font-semibold transition ${
            activeTab === 'presets'
              ? 'bg-emerald-600 text-white shadow'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>1-Click Presets</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('directory')}
          className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg text-xs font-semibold transition ${
            activeTab === 'directory'
              ? 'bg-emerald-600 text-white shadow'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
          }`}
        >
          <FolderSearch className="w-4 h-4" />
          <span>Scan Local Folder</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('upload')}
          className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg text-xs font-semibold transition ${
            activeTab === 'upload'
              ? 'bg-emerald-600 text-white shadow'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
          }`}
        >
          <UploadCloud className="w-4 h-4" />
          <span>Upload Files</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('editor')}
          className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg text-xs font-semibold transition ${
            activeTab === 'editor'
              ? 'bg-emerald-600 text-white shadow'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
          }`}
        >
          <Code2 className="w-4 h-4" />
          <span>Manual Code Editor</span>
        </button>
      </div>

      {/* TAB 1: 1-CLICK PRESETS */}
      {activeTab === 'presets' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-zinc-200 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span>Select a Pre-configured Software Defect</span>
            </h2>
            <span className="text-xs text-zinc-400">Click any card to load instantly</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {presets.map((p) => {
              const isSelected = selectedPresetId === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => applyPreset(p)}
                  className={`p-4 rounded-xl border transition cursor-pointer space-y-3 relative ${
                    isSelected
                      ? 'bg-emerald-950/20 border-emerald-500 shadow-md ring-1 ring-emerald-500/50'
                      : 'bg-zinc-900/60 border-zinc-800 hover:border-zinc-700 hover:bg-zinc-900'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-semibold uppercase">
                        {p.category}
                      </span>
                      <h3 className="text-sm font-bold text-zinc-100 mt-1.5">{p.title}</h3>
                    </div>
                    {isSelected && (
                      <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                    )}
                  </div>

                  <p className="text-xs text-zinc-300 leading-relaxed">{p.description}</p>

                  <div className="p-2.5 rounded bg-zinc-950/70 border border-zinc-800/80 text-[11px] text-emerald-400/90 leading-normal flex items-start gap-2">
                    <span className="font-bold text-emerald-300 shrink-0">💡 Layman Note:</span>
                    <span>{p.layman_story}</span>
                  </div>

                  <div className="pt-1 flex items-center justify-between text-[11px] font-mono text-zinc-400">
                    <span>File: {p.source_file}</span>
                    <span className="text-emerald-400 font-semibold">
                      {isSelected ? '✓ Loaded into Form' : 'Click to Load'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 2: SCAN LOCAL FOLDER PATH */}
      {activeTab === 'directory' && (
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-5 space-y-5">
          <div>
            <h2 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
              <Folder className="w-4 h-4 text-emerald-400" />
              <span>Scan Any Folder on Your Computer</span>
            </h2>
            <p className="text-xs text-zinc-400 mt-1">
              Enter a directory path. The system will inspect your folder, discover Python files, detect test suites, and configure the repair workspace.
            </p>
          </div>

          <form onSubmit={handleScanDirectory} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={dirPathInput}
              onChange={(e) => setDirPathInput(e.target.value)}
              placeholder="e.g. E:\path\to\my_project or examples/regression_demo"
              className="flex-1 bg-zinc-950 border border-zinc-700 rounded-lg px-3.5 py-2.5 text-xs font-mono text-zinc-200 focus:outline-none focus:border-emerald-500"
            />
            <button
              type="submit"
              disabled={scanning}
              className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition shadow-sm"
            >
              {scanning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Scanning...</span>
                </>
              ) : (
                <>
                  <FolderSearch className="w-4 h-4" />
                  <span>Scan Folder</span>
                </>
              )}
            </button>
          </form>

          {/* Quick suggestions */}
          <div className="flex items-center gap-2 text-xs text-zinc-400 flex-wrap">
            <span>Quick Suggestions:</span>
            <button
              type="button"
              onClick={() => {
                setDirPathInput('examples/regression_demo');
              }}
              className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-emerald-400 font-mono text-[11px] transition"
            >
              examples/regression_demo
            </button>
            <button
              type="button"
              onClick={() => {
                setDirPathInput('benchmarks/tasks/01_arithmetic_tax');
              }}
              className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-emerald-400 font-mono text-[11px] transition"
            >
              benchmarks/tasks/01_arithmetic_tax
            </button>
            <button
              type="button"
              onClick={() => {
                setDirPathInput('benchmarks/tasks/03_boundary_binary_search');
              }}
              className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-emerald-400 font-mono text-[11px] transition"
            >
              benchmarks/tasks/03_boundary_binary_search
            </button>
          </div>

          {scanError && (
            <div className="p-3 bg-rose-950/40 border border-rose-800 rounded-lg text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{scanError}</span>
            </div>
          )}

          {scanResult && (
            <div className="bg-zinc-950 p-4 rounded-lg border border-zinc-800 space-y-4">
              <div className="flex items-center justify-between text-xs font-mono text-zinc-300 border-b border-zinc-800 pb-2">
                <span>📁 Discovered in: {scanResult.directory_path}</span>
                <span className="text-emerald-400 font-semibold">
                  {scanResult.source_files.length} Source / {scanResult.test_files.length} Tests
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                {/* Select Source File */}
                <div className="space-y-1.5">
                  <label className="text-zinc-400 font-semibold block">Select File to Repair:</label>
                  <select
                    value={sourceFile}
                    onChange={(e) => {
                      const f = scanResult.source_files.find((s) => s.filename === e.target.value);
                      if (f) {
                        setSourceFile(f.filename);
                        setSourceContent(f.content);
                      }
                    }}
                    className="w-full bg-zinc-900 border border-zinc-700 rounded p-2 text-zinc-200 focus:outline-none"
                  >
                    {scanResult.source_files.map((s) => (
                      <option key={s.filename} value={s.filename}>
                        {s.filename}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Select Target Test File */}
                <div className="space-y-1.5">
                  <label className="text-zinc-400 font-semibold block">Select Failing Target Test File:</label>
                  <select
                    value={testFile}
                    onChange={(e) => {
                      const f = scanResult.test_files.find((s) => s.filename === e.target.value);
                      if (f) {
                        setTestFile(f.filename);
                        setTestContent(f.content);
                        if (f.test_cases.length > 0) {
                          setTargetTest(`${f.filename}::${f.test_cases[0]}`);
                        }
                      }
                    }}
                    className="w-full bg-zinc-900 border border-zinc-700 rounded p-2 text-zinc-200 focus:outline-none"
                  >
                    {scanResult.test_files.map((t) => (
                      <option key={t.filename} value={t.filename}>
                        {t.filename} ({t.test_cases.length} test cases)
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Target Test Spec */}
              <div className="space-y-1.5 text-xs font-mono">
                <label className="text-zinc-400 font-semibold block">Target Pytest Function Spec:</label>
                <input
                  type="text"
                  value={targetTest}
                  onChange={(e) => setTargetTest(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-700 rounded p-2 text-zinc-200 focus:outline-none"
                  placeholder="e.g. test_target.py::test_case"
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: UPLOAD FILES */}
      {activeTab === 'upload' && (
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-5 space-y-6">
          <div>
            <h2 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
              <UploadCloud className="w-4 h-4 text-emerald-400" />
              <span>Upload Your Python Code & Test Files</span>
            </h2>
            <p className="text-xs text-zinc-400 mt-1">
              Select local files from your computer. Files are read securely inside your browser and loaded into the repair pipeline.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* 1. Broken Source File */}
            <div className="bg-zinc-950 p-4 rounded-xl border border-zinc-800 flex flex-col justify-between space-y-3">
              <div>
                <span className="text-[10px] font-mono uppercase text-emerald-400 font-bold block mb-1">
                  Step 1
                </span>
                <h3 className="text-xs font-bold text-zinc-200">Broken Source File (.py)</h3>
                <p className="text-[11px] text-zinc-400 mt-1">The Python module containing the bug you want fixed.</p>
              </div>

              <div className="pt-2">
                <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-zinc-700 hover:border-emerald-500 rounded-lg cursor-pointer bg-zinc-900/40 hover:bg-zinc-900 transition text-center">
                  <FileCode className="w-6 h-6 text-emerald-400 mb-1" />
                  <span className="text-xs text-zinc-300 font-semibold">Choose .py File</span>
                  <span className="text-[10px] text-zinc-500 mt-0.5 truncate max-w-full">
                    {sourceFile ? `Selected: ${sourceFile}` : 'Click to browse'}
                  </span>
                  <input
                    type="file"
                    accept=".py"
                    onChange={(e) => handleFileUpload(e, 'source')}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* 2. Target Failing Test */}
            <div className="bg-zinc-950 p-4 rounded-xl border border-zinc-800 flex flex-col justify-between space-y-3">
              <div>
                <span className="text-[10px] font-mono uppercase text-emerald-400 font-bold block mb-1">
                  Step 2
                </span>
                <h3 className="text-xs font-bold text-zinc-200">Target Failing Test (.py)</h3>
                <p className="text-[11px] text-zinc-400 mt-1">The pytest test that catches the bug and currently fails.</p>
              </div>

              <div className="pt-2">
                <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-zinc-700 hover:border-emerald-500 rounded-lg cursor-pointer bg-zinc-900/40 hover:bg-zinc-900 transition text-center">
                  <FileCode className="w-6 h-6 text-amber-400 mb-1" />
                  <span className="text-xs text-zinc-300 font-semibold">Choose Test File</span>
                  <span className="text-[10px] text-zinc-500 mt-0.5 truncate max-w-full">
                    {testFile ? `Selected: ${testFile}` : 'Click to browse'}
                  </span>
                  <input
                    type="file"
                    accept=".py"
                    onChange={(e) => handleFileUpload(e, 'target_test')}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* 3. Regression Test Suites */}
            <div className="bg-zinc-950 p-4 rounded-xl border border-zinc-800 flex flex-col justify-between space-y-3">
              <div>
                <span className="text-[10px] font-mono uppercase text-emerald-400 font-bold block mb-1">
                  Step 3 (Optional)
                </span>
                <h3 className="text-xs font-bold text-zinc-200">Regression Tests (.py)</h3>
                <p className="text-[11px] text-zinc-400 mt-1">Existing tests that must NEVER break during repair.</p>
              </div>

              <div className="pt-2">
                <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-zinc-700 hover:border-emerald-500 rounded-lg cursor-pointer bg-zinc-900/40 hover:bg-zinc-900 transition text-center">
                  <ShieldCheck className="w-6 h-6 text-indigo-400 mb-1" />
                  <span className="text-xs text-zinc-300 font-semibold">Add Regression Files</span>
                  <span className="text-[10px] text-zinc-500 mt-0.5">
                    {regressionTests.length > 0 ? `${regressionTests.length} file(s) loaded` : 'Select multiple files'}
                  </span>
                  <input
                    type="file"
                    accept=".py"
                    multiple
                    onChange={(e) => handleFileUpload(e, 'regression')}
                    className="hidden"
                  />
                </label>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Code Details & Summary Review Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 rounded-lg bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Source Code Review / Editor */}
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-mono uppercase text-zinc-300 font-bold flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-emerald-400" />
              Source File to Repair
            </label>
            <input
              type="text"
              value={sourceFile}
              onChange={(e) => setSourceFile(e.target.value)}
              className="bg-zinc-950 border border-zinc-700 rounded px-2.5 py-1 text-xs font-mono text-zinc-200 w-64 focus:outline-none focus:border-emerald-500"
              placeholder="e.g. buggy_module.py"
              required
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-zinc-400 font-mono">Code Content:</span>
              <span className="text-[10px] text-zinc-500 font-mono">{sourceContent ? sourceContent.split('\n').length : 0} lines</span>
            </div>
            <textarea
              rows={7}
              value={sourceContent}
              onChange={(e) => setSourceContent(e.target.value)}
              placeholder="def calculate_discounted_price(price, discount): ..."
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-xs font-mono text-zinc-200 focus:outline-none focus:border-emerald-500 leading-relaxed"
              required
            />
          </div>
        </div>

        {/* Target Test Spec Review / Editor */}
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-5 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-mono uppercase text-zinc-300 font-bold block mb-1">
                Target Test File Name
              </label>
              <input
                type="text"
                value={testFile}
                onChange={(e) => setTestFile(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded px-2.5 py-1.5 text-xs font-mono text-zinc-200 focus:outline-none focus:border-emerald-500"
                placeholder="e.g. test_target.py"
                required
              />
            </div>
            <div>
              <label className="text-xs font-mono uppercase text-zinc-300 font-bold block mb-1">
                Target Pytest Spec (Function to Pass)
              </label>
              <input
                type="text"
                value={targetTest}
                onChange={(e) => setTargetTest(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded px-2.5 py-1.5 text-xs font-mono text-zinc-200 focus:outline-none focus:border-emerald-500"
                placeholder="e.g. test_target.py::test_case"
                required
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-zinc-400 font-mono">Target Test Code:</span>
              <span className="text-[10px] text-zinc-500 font-mono">{testContent ? testContent.split('\n').length : 0} lines</span>
            </div>
            <textarea
              rows={5}
              value={testContent}
              onChange={(e) => setTestContent(e.target.value)}
              placeholder="def test_discount(): ..."
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-xs font-mono text-zinc-200 focus:outline-none focus:border-emerald-500 leading-relaxed"
              required
            />
          </div>
        </div>

        {/* Existing Regression Suites */}
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xs font-mono uppercase text-zinc-300 font-bold flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-indigo-400" />
                Regression Test Suites ({regressionTests.length})
              </h3>
              <p className="text-xs text-zinc-400">
                Tests that guarantee existing behavior is NOT broken during repair.
              </p>
            </div>
            <button
              type="button"
              onClick={handleAddRegressionFile}
              className="flex items-center gap-1.5 px-3 py-1 rounded bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-xs font-mono text-zinc-200 transition"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Suite</span>
            </button>
          </div>

          {regressionTests.map((reg, idx) => (
            <div key={idx} className="p-3 bg-zinc-950/80 rounded-lg border border-zinc-800 space-y-2">
              <div className="flex items-center justify-between">
                <input
                  type="text"
                  value={reg.filename}
                  onChange={(e) => {
                    const copy = [...regressionTests];
                    copy[idx].filename = e.target.value;
                    setRegressionTests(copy);
                  }}
                  className="bg-zinc-900 border border-zinc-700 rounded px-2 py-0.5 text-xs font-mono text-zinc-200 w-64"
                />
                <button
                  type="button"
                  onClick={() => handleRemoveRegressionFile(idx)}
                  className="text-zinc-500 hover:text-rose-400 p-1"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
              <textarea
                rows={3}
                value={reg.content}
                onChange={(e) => {
                  const copy = [...regressionTests];
                  copy[idx].content = e.target.value;
                  setRegressionTests(copy);
                }}
                placeholder="# regression tests..."
                className="w-full bg-zinc-900 border border-zinc-800 rounded p-2 text-xs font-mono text-zinc-200"
              />
            </div>
          ))}
        </div>

        {/* Configuration Bar */}
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-6 flex-wrap">
            <div>
              <span className="text-xs font-mono text-zinc-400 block mb-1 font-semibold">
                Max Allowed Attempts:
              </span>
              <div className="flex items-center gap-1.5 font-mono text-xs">
                {[1, 2, 3, 4, 5].map((num) => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => setMaxAttempts(num)}
                    className={`w-7 h-7 rounded border font-semibold transition ${
                      maxAttempts === num
                        ? 'bg-emerald-600 border-emerald-500 text-white shadow'
                        : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200'
                    }`}
                  >
                    {num}
                  </button>
                ))}
              </div>
            </div>

            <label className="flex items-center gap-2 cursor-pointer mt-3 sm:mt-0">
              <input
                type="checkbox"
                checked={useMock}
                onChange={(e) => setUseMock(e.target.checked)}
                className="rounded bg-zinc-950 border-zinc-700 text-emerald-500 focus:ring-0 focus:ring-offset-0"
              />
              <span className="text-xs font-mono text-zinc-300">
                Mock Mode (Instant local run without API costs)
              </span>
            </label>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm font-mono transition shadow-lg shadow-emerald-950/50 disabled:opacity-50"
          >
            {submitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Initializing Sandbox...</span>
              </>
            ) : (
              <>
                <PlayCircle className="w-5 h-5" />
                <span>START AUTONOMOUS REPAIR</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
