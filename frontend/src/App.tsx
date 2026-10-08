import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { NewRepair } from './pages/NewRepair';
import { LiveRepair } from './pages/LiveRepair';
import { Benchmarks } from './pages/Benchmarks';
import { Observability } from './pages/Observability';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/new" element={<NewRepair />} />
            <Route path="/repairs/:id" element={<LiveRepair />} />
            <Route path="/benchmarks" element={<Benchmarks />} />
            <Route path="/observability" element={<Observability />} />
          </Routes>
        </main>
        <footer className="border-t border-zinc-900 bg-zinc-950/60 py-6 text-center text-xs font-mono text-zinc-500">
          Self-Healing Code Repair Pipeline • LangGraph + Native Groq Tool Calling + Docker Sandbox
        </footer>
      </div>
    </BrowserRouter>
  );
};

export default App;
