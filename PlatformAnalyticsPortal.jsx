import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Layers, 
  Database, 
  Cpu, 
  ExternalLink, 
  ArrowRight, 
  CheckCircle2, 
  Activity, 
  BarChart3, 
  Server
} from 'lucide-react';

/**
 * Official Databricks Brand Icon (SVG)
 */
function DatabricksIcon({ className = "w-5 h-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#FF3621" />
      <path d="M2 12L12 17L22 12" stroke="#FF3621" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M2 17L12 22L22 17" stroke="#FF3621" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/**
 * Enterprise Cloud SQL Database Icon (SVG)
 */
function SqlDatabaseIcon({ className = "w-5 h-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <ellipse cx="12" cy="5" rx="9" ry="3" fill="#0284C7" fillOpacity="0.3" stroke="#38BDF8" />
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" stroke="#38BDF8" />
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" stroke="#38BDF8" />
      <path d="M12 12v3" stroke="#38BDF8" strokeWidth="1.5" strokeDasharray="2 2" />
    </svg>
  );
}

/**
 * Analytics in Platform - Executive Architecture & Portals
 * LifePro first, MedConnection second. Clean static status dots, no settings clutter.
 */
export function PlatformAnalyticsPortal({ onSelectMedCon }) {
  // Configurable LifePro URL
  const [lifeProUrl] = useState(() => {
    return localStorage.getItem("exl_lifepro_url") || "https://lifepro.exlservice.com";
  });

  // LifePro 3 Bullet Points (Names only)
  const lifeProPoints = [
    "Policy Administration & Ingestion",
    "Actuarial & Underwriting Risk Modeling",
    "Prescriptive Portfolio Analytics"
  ];

  const handleLaunchLifePro = () => {
    window.open(lifeProUrl, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="h-screen w-screen bg-[#060D1A] text-slate-100 flex flex-col justify-between overflow-hidden selection:bg-[#FF5B35] selection:text-white relative font-sans">
      {/* EXL Corporate Ambient Gradients */}
      <div className="absolute top-[-10%] left-[10%] w-[650px] h-[650px] rounded-full bg-[#FF5B35]/10 blur-[170px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[10%] w-[650px] h-[650px] rounded-full bg-[#FF5B35]/8 blur-[170px] pointer-events-none" />

      {/* ========================================================================= */}
      {/* 1. TOP CORPORATE HEADER                                                  */}
      {/* ========================================================================= */}
      <header className="shrink-0 h-14 border-b border-slate-800/80 bg-[#081226]/95 backdrop-blur-md px-8 flex justify-between items-center z-20">
        <div className="flex items-center space-x-3">
          {/* Authentic EXL Brand Wordmark */}
          <div className="flex items-center space-x-2.5">
            <div className="h-8 px-3.5 rounded bg-[#FF5B35] flex items-center justify-center font-black text-white text-base tracking-wider shadow-md shadow-[#FF5B35]/30 font-heading">
              EXL
            </div>
            <div className="h-5 w-[1px] bg-slate-700" />
            <div className="flex flex-col">
              <span className="text-xs font-bold text-white tracking-wide uppercase font-heading">
                Analytics in Platform
              </span>
              <span className="text-[10px] text-slate-400 font-medium">
                Enterprise AI & Decision Solutions
              </span>
            </div>
          </div>
        </div>

        {/* Global Operational Status */}
        <div className="flex items-center space-x-2 px-3.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          <span className="text-slate-300 font-semibold text-[11px] tracking-wider uppercase">
            Analytics-Led Platform Ecosystem
          </span>
        </div>
      </header>

      {/* ========================================================================= */}
      {/* 2. MAIN WORKSPACE (TIGHTLY CONNECTED TO PLATFORMS)                        */}
      {/* ========================================================================= */}
      <main className="flex-1 w-full px-8 py-2 flex flex-col justify-between z-10">
        
        {/* Page Hero Header */}
        <div className="text-center space-y-1 mb-1">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight leading-tight">
            Analytics in Platform
          </h1>
          <p className="text-sm sm:text-base text-slate-200 max-w-3xl mx-auto font-normal leading-snug">
            Operationalizing core transactional platforms into unified enterprise Data Marts, advanced predictive modeling, and prescriptive decision intelligence.
          </p>
        </div>

        {/* ========================================================================= */}
        {/* 3. TWIN PLATFORMS: LIFEPRO FIRST, MEDCON SECOND                           */}
        {/* ========================================================================= */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full max-w-7xl mx-auto items-stretch my-1">
          
          {/* ----------------------------------------------------------------------- */}
          {/* PLATFORM 1: LIFEPRO (MATCHED CARD DIMENSIONS & TYPOGRAPHY)               */}
          {/* ----------------------------------------------------------------------- */}
          <div className="bg-[#0A1428]/60 border-2 border-slate-700/70 rounded-xl p-6 shadow-2xl shadow-black/40 flex flex-col justify-between relative group opacity-85 hover:opacity-100 transition-all">
            <div className="space-y-4">
              
              {/* Card Header: Platform Title & Subtitle */}
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center space-x-3.5">
                  <div className="h-12 w-12 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 shadow-lg shrink-0">
                    <ShieldCheck className="w-7 h-7" />
                  </div>
                  <div>
                    <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">LifePro</h2>
                    <p className="text-lg text-slate-100 font-bold pt-0.5 leading-snug">
                      LifePro Analytics module
                    </p>
                  </div>
                </div>
              </div>

              {/* 3 Bullet Points */}
              <div className="py-2 space-y-3">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Core Capabilities
                </div>

                <ul className="space-y-3 pl-1">
                  {lifeProPoints.map((pt, idx) => (
                    <li key={idx} className="flex items-center space-x-3">
                      <span className="h-2.5 w-2.5 rounded-full bg-slate-500 shrink-0" />
                      <span className="text-base font-bold text-white tracking-wide">
                        {pt}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Lines of Business (LOB) Section */}
              <div className="pt-3 border-t border-slate-800 space-y-2">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                  <Layers className="w-4 h-4 text-emerald-400" />
                  <span>Lines of Business (LOB)</span>
                </div>

                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs pl-1">
                  <div className="inline-flex items-center space-x-1.5 text-emerald-300 font-bold text-sm">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>Life and Annuity</span>
                  </div>
                </div>
              </div>

            </div>

            {/* Launch Life Pro Button */}
            <div className="pt-4 mt-1">
              <button
                onClick={handleLaunchLifePro}
                className="w-full py-4 px-4 rounded-lg bg-slate-800/90 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 text-slate-200 hover:text-white font-black text-lg sm:text-xl tracking-wide shadow-md transition-all flex items-center justify-center space-x-3 cursor-pointer"
              >
                <span>Launch Life Pro Platform</span>
                <ExternalLink className="w-6 h-6 text-slate-400" />
              </button>
            </div>
          </div>

          {/* ----------------------------------------------------------------------- */}
          {/* PLATFORM 2: MEDCONNECTION (HIGHLIGHTED)                                  */}
          {/* ----------------------------------------------------------------------- */}
          <div className="bg-[#0A1428] border-2 border-[#FF5B35] rounded-xl p-6 shadow-2xl shadow-[#FF5B35]/25 ring-1 ring-[#FF5B35]/30 flex flex-col justify-between relative group transition-all transform hover:scale-[1.008]">
            <div className="space-y-4">
              
              {/* Card Header: Platform Title & Subtitle */}
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center space-x-3.5">
                  <div className="h-12 w-12 rounded-lg bg-[#FF5B35]/25 border border-[#FF5B35]/60 flex items-center justify-center text-[#FF5B35] shadow-lg shadow-[#FF5B35]/20 shrink-0">
                    <Activity className="w-7 h-7" />
                  </div>
                  <div>
                    <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">MedConnection</h2>
                    <p className="text-lg text-slate-100 font-bold pt-0.5 leading-snug">
                      Medical Complexity and Severity Analytics Intelligence Platform
                    </p>
                  </div>
                </div>
              </div>

              {/* 4 Core Capabilities with Existing / New Tags */}
              <div className="py-2 space-y-2.5">
                <div className="text-xs font-bold uppercase tracking-wider text-[#FF5B35]">
                  Core Capabilities
                </div>

                <ul className="space-y-2.5 pl-1">
                  {/* 1. AI Extraction and Summarization: Existing */}
                  <li className="flex items-center justify-between pr-2">
                    <div className="flex items-center space-x-3">
                      <span className="h-2.5 w-2.5 rounded-full bg-slate-400 shrink-0" />
                      <span className="text-base font-bold text-white tracking-wide">
                        AI Extraction and Summarization
                      </span>
                    </div>
                    <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                      Existing
                    </span>
                  </li>

                  {/* 2. Complexity Score Modeling: New */}
                  <li className="flex items-center justify-between pr-2">
                    <div className="flex items-center space-x-3">
                      <span className="h-2.5 w-2.5 rounded-full bg-[#FF5B35] shrink-0" />
                      <span className="text-base font-bold text-white tracking-wide">
                        Complexity Score Modeling
                      </span>
                    </div>
                    <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#FF5B35]/20 border border-[#FF5B35]/60 text-[#FFA17A]">
                      New
                    </span>
                  </li>

                  {/* 3. Severity Calculation: New */}
                  <li className="flex items-center justify-between pr-2">
                    <div className="flex items-center space-x-3">
                      <span className="h-2.5 w-2.5 rounded-full bg-[#FF5B35] shrink-0" />
                      <span className="text-base font-bold text-white tracking-wide">
                        Severity Calculation
                      </span>
                    </div>
                    <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#FF5B35]/20 border border-[#FF5B35]/60 text-[#FFA17A]">
                      New
                    </span>
                  </li>

                  {/* 4. Prescriptive Cost Attribution: New */}
                  <li className="flex items-center justify-between pr-2">
                    <div className="flex items-center space-x-3">
                      <span className="h-2.5 w-2.5 rounded-full bg-[#FF5B35] shrink-0" />
                      <span className="text-base font-bold text-white tracking-wide">
                        Prescriptive Cost Attribution
                      </span>
                    </div>
                    <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#FF5B35]/20 border border-[#FF5B35]/60 text-[#FFA17A]">
                      New
                    </span>
                  </li>
                </ul>
              </div>

              {/* Lines of Business (LOB) Section with Active & Grayed Out LOBs */}
              <div className="pt-3 border-t border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                    <Layers className="w-4 h-4 text-emerald-400" />
                    <span>Medical Claim Lines of Business (LOB)</span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-medium">
                    Clinical &amp; Injury Severity Focus
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs pl-1">
                  {/* Active 1: Commercial Auto */}
                  <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 font-bold text-xs shadow-sm">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span>Commercial Auto</span>
                  </div>

                  {/* Active 2: Personal Auto */}
                  <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 font-bold text-xs shadow-sm">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span>Personal Auto</span>
                  </div>

                  {/* Active 3: General Liability (GL) */}
                  <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 font-bold text-xs shadow-sm">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span>General Liability (GL)</span>
                  </div>

                  {/* Active 4: Workers' Comp */}
                  <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 font-bold text-xs shadow-sm">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span>Workers' Comp</span>
                  </div>

                  {/* Grayed-out LOBs */}
                  {/* 1. Medical Care Underwriting (MCU) */}
                  <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900/60 border border-slate-800 text-slate-500 font-medium text-xs opacity-75">
                    <span className="h-1.5 w-1.5 rounded-full bg-slate-600 shrink-0" />
                    <span>MCU (Medical Care Underwriting)</span>
                  </div>

                  {/* 2. Swift Auto */}
                  <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900/60 border border-slate-800 text-slate-500 font-medium text-xs opacity-75">
                    <span className="h-1.5 w-1.5 rounded-full bg-slate-600 shrink-0" />
                    <span>Swift Auto</span>
                  </div>

                  {/* 3. Swift GL */}
                  <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900/60 border border-slate-800 text-slate-500 font-medium text-xs opacity-75">
                    <span className="h-1.5 w-1.5 rounded-full bg-slate-600 shrink-0" />
                    <span>Swift GL</span>
                  </div>
                </div>
              </div>

            </div>

            {/* Launch Button (Vibrant EXL Orange with Updated Text) */}
            <div className="pt-4 mt-1">
              <button
                onClick={onSelectMedCon}
                className="w-full py-4 px-4 rounded-lg bg-gradient-to-r from-[#FF5B35] to-[#FF4500] hover:from-[#FF6B45] hover:to-[#FF5B35] text-white font-black text-lg sm:text-xl tracking-wide shadow-xl shadow-[#FF5B35]/35 transition-all flex items-center justify-center space-x-3 cursor-pointer border border-[#FF8A65]/70 ring-2 ring-[#FF5B35]/30 hover:ring-[#FF5B35]/60"
              >
                <span>Launch MedConnection Intelligence Platform</span>
                <ArrowRight className="w-6 h-6 stroke-[3]" />
              </button>
            </div>
          </div>

        </div>

        {/* ========================================================================= */}
        {/* 4. SUBTLE ARCHITECTURE FLOW (LIFEPRO TOP, MEDCON BOTTOM, 2 ARROWS)         */}
        {/* ========================================================================= */}
        <div className="w-full bg-[#081120]/75 border border-slate-800/60 rounded-xl px-6 py-2.5 shadow-md relative mt-1">
          
          {/* Subtle Header */}
          <div className="flex items-center justify-between pb-1.5 mb-1.5 border-b border-slate-800/60">
            <div className="flex items-center space-x-2">
              <Server className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Enterprise Data Mart & Decision Flow Architecture
              </span>
            </div>
            <span className="text-[10px] text-slate-500">
              Internal Architecture
            </span>
          </div>

          {/* Architecture Flow Canvas */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 py-1">
            
            {/* 1. PLATFORM (Just Platform in a box) */}
            <div className="px-5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-center shrink-0 shadow-sm">
              <span className="text-sm font-bold text-white tracking-wide">Platform</span>
            </div>

            {/* CONNECTOR 1: Flow Arrow to Data Mart */}
            <div className="hidden md:flex items-center text-slate-500 px-2 shrink-0">
              <div className="h-[2px] w-20 bg-slate-700" />
              <ArrowRight className="w-4 h-4 text-slate-400 -ml-1 shrink-0" />
            </div>

            {/* 2. DATA MART (with Databricks & SQL) */}
            <div className="px-6 py-2 rounded-lg bg-slate-900 border border-sky-500/40 text-center flex flex-col items-center space-y-1 shrink-0 shadow-sm">
              <div className="flex items-center space-x-1.5 text-sky-400 font-bold text-xs uppercase tracking-wider">
                <Database className="w-3.5 h-3.5 text-sky-400" />
                <span>Data Mart</span>
              </div>

              {/* Databricks & SQL mentioned clearly */}
              <div className="flex items-center space-x-4 pt-0.5">
                <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-200">
                  <DatabricksIcon className="w-4 h-4" />
                  <span>Databricks</span>
                </div>
                <div className="h-3 w-[1px] bg-slate-700" />
                <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-200">
                  <SqlDatabaseIcon className="w-4 h-4" />
                  <span>SQL</span>
                </div>
              </div>
            </div>

            {/* CONNECTOR 2: TWO DISTINCT ARROWS BRANCHING TO MODELING AGENT & PRESCRIPTIVE BI */}
            <div className="hidden md:flex flex-col justify-center space-y-3 px-2 shrink-0">
              {/* Arrow 1 -> Modeling Agent */}
              <div className="flex items-center text-slate-500">
                <div className="h-[2px] w-16 bg-gradient-to-r from-sky-400 to-purple-400" />
                <ArrowRight className="w-3.5 h-3.5 text-purple-400 -ml-1 shrink-0" />
              </div>
              {/* Arrow 2 -> Prescriptive BI */}
              <div className="flex items-center text-slate-500">
                <div className="h-[2px] w-16 bg-gradient-to-r from-sky-400 to-emerald-400" />
                <ArrowRight className="w-3.5 h-3.5 text-emerald-400 -ml-1 shrink-0" />
              </div>
            </div>

            {/* 3. TWO DESTINATIONS: MODELING AGENT & PRESCRIPTIVE BI */}
            <div className="flex flex-col space-y-2 shrink-0 text-left">
              {/* Destination 1: Modeling Agent */}
              <div className="px-4 py-1.5 rounded-lg bg-slate-900 border border-purple-500/40 flex items-center space-x-2 shadow-sm">
                <Cpu className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                <span className="text-xs font-bold text-white tracking-wide">Modeling Agent</span>
              </div>

              {/* Destination 2: Prescriptive BI */}
              <div className="px-4 py-1.5 rounded-lg bg-slate-900 border border-emerald-500/40 flex items-center space-x-2 shadow-sm">
                <BarChart3 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span className="text-xs font-bold text-white tracking-wide">Prescriptive BI</span>
              </div>
            </div>

          </div>
        </div>

      </main>

      {/* ========================================================================= */}
      {/* 5. SLIM CLEAN CORPORATE FOOTER                                            */}
      {/* ========================================================================= */}
      <footer className="shrink-0 text-center py-2 border-t border-slate-800/80 bg-[#060D1A] text-[11px] text-slate-400">
        <span>EXL Service • Analytics in Platform • Casualty & Life Decision Architecture</span>
      </footer>

    </div>
  );
}
export default PlatformAnalyticsPortal;
