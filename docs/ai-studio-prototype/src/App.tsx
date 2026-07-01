/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, FormEvent } from 'react';
import { 
  FolderIcon, 
  FileCodeIcon, 
  TerminalIcon, 
  ActivityIcon, 
  DatabaseIcon, 
  NetworkIcon, 
  TrendingUpIcon, 
  LayersIcon, 
  CheckCircle2Icon, 
  CopyIcon, 
  CheckIcon,
  ChevronRightIcon, 
  ArrowRightIcon, 
  LeafIcon, 
  UsersIcon, 
  ShieldCheckIcon,
  InfoIcon,
  BookOpenIcon
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

// Definitions for the file contents we created to display in the Scaffold tab
const SCAFFOLD_FILES = [
  {
    path: 'app/main.py',
    label: 'main.py',
    description: 'FastAPI entry point and middleware configuration',
    lang: 'python',
    content: `from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import health

# Intialize the FastAPI application
app = FastAPI(
    title="Mbhewoo Labs API",
    description="Collaborative credibility forecasting platform for African biomedical and biotechnology research",
    version="0.1.0",
)

# Apply CORS middleware for API routing and external interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints and routers
app.include_router(health.router)


@app.get("/")
async def root():
    """
    Root greeting metadata.
    """
    return {
        "message": "Welcome to Mbhewoo Labs - African Biomedical & Biotechnology Credibility Platform",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    # Local fallback execution runner
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
`
  },
  {
    path: 'app/config.py',
    label: 'config.py',
    description: 'Pydantic Settings configurations loading from .env',
    lang: 'python',
    content: `from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Application settings for Mbhewoo Labs.
    Loads and validates values from environment variables or a .env file.
    """
    # Environment mode
    ENVIRONMENT: Literal["dev", "prod"] = "dev"
    
    # Security Key for cryptographic signings and credentials
    SECRET_KEY: str = "dev_secret_key_change_me_in_production_1234567890"

    # Supabase / PostgreSQL Connection Database URL (compatible with asyncpg)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mbhewoo_labs"

    # Neo4j Database configuration values
    NEO4J_URI: str = "neo4j://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Pydantic Settings configuration meta-class
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore any other environment variables not defined here
    )


# Instantiate the settings container
settings = Settings()
`
  },
  {
    path: 'app/database.py',
    label: 'database.py',
    description: 'PostgreSQL SQLAlchemy Engine + Neo4j driver initialization',
    lang: 'python',
    content: `from collections.abc import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from neo4j import GraphDatabase, Driver

from app.config import settings

# --- SQLAlchemy Setup ---
# Create async engine for PostgreSQL (using asyncpg)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True if settings.ENVIRONMENT == "dev" else False,
    future=True,
    pool_size=10,
    max_overflow=20,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Declarative base class for models
Base = declarative_base()


# Dependency injection helper for FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a new SQLAlchemy AsyncSession.
    Ensures safe automatic closure when the request lifecycle ends.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# --- Neo4j Setup ---
# Instantiate the Neo4j Driver (Graph Database)
# Driver objects handle connection pools internally and should be instantiated globally
neo4j_driver: Driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
)


def get_neo4j() -> Generator[Driver, None, None]:
    """
    Get the Neo4j global driver instance.
    The driver is a thread-safe singleton that coordinates connection pools.
    """
    try:
        yield neo4j_driver
    finally:
        pass
`
  },
  {
    path: 'app/routes/health.py',
    label: 'routes/health.py',
    description: 'Primary router targeting health and live criteria',
    lang: 'python',
    content: `from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Service health check endpoint.
    Verifies that the application server is up, running, and accessible.
    """
    return {
        "status": "ok",
        "service": "mbhewoo-labs",
    }
`
  },
  {
    path: 'app/templates/base.html',
    label: 'templates/base.html',
    description: 'Base Jinja2 HTML layout embedded with HTMX + Live Tailwind',
    lang: 'html',
    content: `<!DOCTYPE html>
<html lang="en" class="h-full bg-slate-50">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Mbhewoo Labs{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        brand: {
                            50: '#f0fbf6', 100: '#dcf7ea', 200: '#bbeed5', 300: '#8adeb5',
                            400: '#52c68e', 500: '#2da872', 600: '#20875c', 700: '#1c6c4c',
                            800: '#1b563f', 900: '#174735', 950: '#0b281f',
                        }
                    }
                }
            }
        }
    </script>
    <script src="https://unpkg.com/htmx.org@1.9.12"></script>
</head>
<body class="h-full text-slate-800 flex flex-col font-sans">
    <header class="border-b border-slate-200 bg-white">
        <!-- Embedded HTMX & Tailwind header layout -->
    </header>
    <main class="flex-1 mx-auto max-w-7xl px-4 py-8 w-full">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
`
  },
  {
    path: 'tests/test_health.py',
    label: 'test_health.py',
    description: 'Pytest testing suite asserting health and payload keys',
    lang: 'python',
    content: `from fastapi.testclient import TestClient
from app.main import app

# Initialize the pytest TestClient targeted at our app instance
client = TestClient(app)


def test_health_check_endpoint():
    """
    Assert that hitting the GET /health router endpoint returns 
    a successful 200 OK standard status code and the correct payload envelope.
    """
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "mbhewoo-labs"
`
  },
  {
    path: 'pyproject.toml',
    label: 'pyproject.toml',
    description: 'Modern PEP 621 Python config and test environment options',
    lang: 'toml',
    content: `[build-system]
requires = ["setuptools>=61.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mbhewoo-labs"
version = "0.1.0"
description = "Credibility forecasting platform for African biomedical and biotechnology research"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.30.1",
    "pydantic>=2.7.4",
    "pydantic-settings>=2.3.3",
    "sqlalchemy[asyncio]>=2.0.31",
    "asyncpg>=0.29.0",
    "neo4j>=5.21.0",
    "Jinja2>=3.1.4",
    "python-dotenv>=1.0.1",
]
`
  },
  {
    path: '.env.example',
    label: '.env.example',
    description: 'Secure placeholders for Supabase SQL and Neo4j Aura secrets',
    lang: 'bash',
    content: `# Mbhewoo Labs - Environment Configurations
ENVIRONMENT=dev
SECRET_KEY=dev_secret_key_change_me_in_production_1234567890

# Postgres Target (e.g. Supabase DB URL with asyncpg)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mbhewoo_labs

# Neo4j Target (e.g. Neo4j AuraDB URI)
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
`
  }
];

// Mock African Biomedical Biotechnology hypotheses being polled on the platform
const MOCK_HYPOTHESES = [
  {
    id: 'hyp-001',
    title: 'Efficacy metrics for Malaria vaccine candidate R21 matrix-M in pediatric cohorts (Phase III RCT in Burkina Faso)',
    author: 'African Malaria Research Consortium',
    category: 'Clinical Trials',
    publicationRef: 'Journal of Medicine & Biology IP-204',
    consensusProbability: 84,  // Derived from pool state
    totalPooledSeeds: 18450,
    activeForecasters: 42,
    credibilityHistory: [70, 72, 75, 78, 83, 84],
    trend: 'rising',
    abstract: 'Investigating whether vaccine formulations targeting circumsporozoite peptide structures sustain sterile protective Immunity above 75% over 18-month intervals.'
  },
  {
    id: 'hyp-002',
    title: 'CRISPR-Cas9 therapeutic fidelity targeting deletion of SCD genomic sequence in multi-center clinical trials',
    author: 'Institute of Hominid Genomics, Lagos',
    category: 'Genomics & Drug Discovery',
    publicationRef: 'West African BioTech Review 2026',
    consensusProbability: 61,
    totalPooledSeeds: 32000,
    activeForecasters: 88,
    credibilityHistory: [50, 52, 55, 59, 62, 61],
    trend: 'stable',
    abstract: 'Fidelity benchmarks and off-target characterization of base-editors configured with sub-genomic guides targeting primary erythroid progenitors.'
  },
  {
    id: 'hyp-003',
    title: 'Bioprocessing throughput metrics of engineered micro-algae lipid extraction yielding anti-retroviral adjuvants',
    author: 'Kigali Biofuel & Pharmacy Lab',
    category: 'Bioprocessing',
    publicationRef: 'Nature Biotechnology Africa (Ahead of Print)',
    consensusProbability: 42,
    totalPooledSeeds: 12100,
    activeForecasters: 29,
    credibilityHistory: [60, 55, 50, 47, 44, 42],
    trend: 'falling',
    abstract: 'Claimed 4-fold increase in dry-mass metabolic separation of specific glycolipids utilizing local gravity-fed bioreactor prototypes.'
  },
  {
    id: 'hyp-004',
    title: 'Functional verification of genomics markers predicting rapid tuberculosis multi-drug resistance (MDR) mutations',
    author: 'Yamoussoukro Biodefense Laboratory',
    category: 'Biotech Diagnosis',
    publicationRef: 'Ivorian Clinical Journal T-11',
    consensusProbability: 73,
    totalPooledSeeds: 9400,
    activeForecasters: 18,
    credibilityHistory: [68, 69, 71, 72, 72, 73],
    trend: 'rising',
    abstract: 'Validation check on structural genomic variant loci in isoniazid-resistant strains cultured within sub-Saharan environments.'
  }
];

// Co-citation node mappings representing Neo4j relationships (for visualization simulator)
const MOCK_GRAPH_NODES = [
  { id: 'R21', label: 'R21 Malaria Trial', type: 'ClinicalTrial', size: 24, group: 1 },
  { id: 'WHO_Standard', label: 'WHO 75% Benchmark', type: 'PolicyGuideline', size: 16, group: 1 },
  { id: 'Lagos_SCD', label: 'Lagos SCD CRISPR', type: 'GenomicsPaper', size: 20, group: 2 },
  { id: 'CRISPR_Base', label: 'CRISPR Base Editing', type: 'Technology', size: 14, group: 2 },
  { id: 'Kigali_Algae', label: 'Kigali Algae Lipid', type: 'Bioprocessing', size: 18, group: 3 },
  { id: 'MDR_TB', label: 'MDR Tuberculosis Genom', type: 'BiotechDiagnosis', size: 18, group: 4 },
  { id: 'OpenAlex_Seed', label: 'OpenAlex Academic Index', type: 'ExternalData', size: 12, group: 5 }
];

const MOCK_GRAPH_LINKS = [
  { source: 'R21', target: 'WHO_Standard', relationship: 'BENCHMARKED_AGAINST' },
  { source: 'Lagos_SCD', target: 'CRISPR_Base', relationship: 'UTILIZES_TECH' },
  { source: 'R21', target: 'OpenAlex_Seed', relationship: 'INDEXED_IN' },
  { source: 'Lagos_SCD', target: 'OpenAlex_Seed', relationship: 'INDEXED_IN' },
  { source: 'Kigali_Algae', target: 'OpenAlex_Seed', relationship: 'INDEXED_IN' },
  { source: 'MDR_TB', target: 'OpenAlex_Seed', relationship: 'INDEXED_IN' },
  { source: 'MDR_TB', target: 'R21', relationship: 'CO_AUTHOR_INSTITUTION' },
  { source: 'Kigali_Algae', target: 'CRISPR_Base', relationship: 'CLONING_MUTATION' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'graph' | 'scaffold' | 'handbook'>('dashboard');
  
  // State for Scaffold panel
  const [selectedFileIdx, setSelectedFileIdx] = useState(0);
  const [copiedFile, setCopiedFile] = useState<string | null>(null);

  // State for market prediction simulation
  const [selectedHypothesis, setSelectedHypothesis] = useState(MOCK_HYPOTHESES[0]);
  const [predictionSide, setPredictionSide] = useState<'YES' | 'NO'>('YES');
  const [seedTradeAmount, setSeedTradeAmount] = useState<number>(250);
  const [userSeedsBalance, setUserSeedsBalance] = useState<number>(5000);
  const [simulatedReceipt, setSimulatedReceipt] = useState<{
    sharesGained: number;
    newConsensus: number;
    slippage: number;
    txHash: string;
  } | null>(null);

  const handleCopyCode = (text: string, path: string) => {
    navigator.clipboard.writeText(text);
    setCopiedFile(path);
    setTimeout(() => setCopiedFile(null), 2000);
  };

  // Logarithmic Market Scoring Rule (LMSR) calculations
  // Minimal b-parameter sizing representing liquidity
  const bMultiplier = 400; 
  const handleSimulateTrade = (e: React.FormEvent) => {
    e.preventDefault();
    if (seedTradeAmount <= 0 || seedTradeAmount > userSeedsBalance) return;

    const isYes = predictionSide === 'YES';
    const currentProb = selectedHypothesis.consensusProbability / 100;
    
    // Virtual shares returned by the score engine
    const shares = Math.round((seedTradeAmount / (isYes ? currentProb : (1 - currentProb))) * 0.95);
    const impact = isYes ? (1 - currentProb) * 0.15 : -currentProb * 0.15;
    const rawNewConsensus = Math.max(10, Math.min(98, Math.round((currentProb + impact) * 100)));
    
    const randomHash = 'tx_' + Math.random().toString(36).substring(2, 10).toUpperCase() + '_seed';

    setSimulatedReceipt({
      sharesGained: shares,
      newConsensus: rawNewConsensus,
      slippage: Math.abs(parseFloat((impact * 5).toFixed(2))),
      txHash: randomHash
    });

    // Update balances and current hypothesis state
    setUserSeedsBalance(prev => prev - seedTradeAmount);
    setSelectedHypothesis(prev => ({
      ...prev,
      consensusProbability: rawNewConsensus,
      totalPooledSeeds: prev.totalPooledSeeds + seedTradeAmount,
      activeForecasters: prev.activeForecasters + 1,
      credibilityHistory: [...prev.credibilityHistory, rawNewConsensus]
    }));
  };

  const handleResetSimulation = () => {
    setSimulatedReceipt(null);
    setSeedTradeAmount(250);
  };

  return (
    <div className="min-h-screen bg-[#0d151c] text-slate-100 flex flex-col font-sans antialiased selection:bg-emerald-500/30 selection:text-emerald-300">
      
      {/* Top Banner Navigation Header */}
      <header className="border-b border-slate-800 bg-[#0d131a]/85 backdrop-blur sticky top-0 z-50 px-4 py-3 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 flex items-center justify-center rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 font-mono text-slate-900 font-black text-xl tracking-tight shadow-md shadow-emerald-500/10">
              Mb
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-white font-mono">Mbhewoo Labs</h1>
                <span className="bg-emerald-500/10 border border-emerald-500/30 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wide text-emerald-400 uppercase">
                  Seed Phase
                </span>
              </div>
              <p className="text-xs text-slate-400">African Biomedical Research Credibility & Forecasting</p>
            </div>
          </div>

          {/* Quick status controls */}
          <div className="flex items-center gap-3 self-end sm:self-auto text-xs font-mono">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-slate-300">Py 3.13 Host (Port 3000)</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/20 border border-emerald-800/20 text-emerald-400">
              <DatabaseIcon className="h-3 w-3" />
              <span>Neo4j + Supabase Configured</span>
            </div>
          </div>
        </div>
      </header>

      {/* Primary Navigation Tabs */}
      <div className="bg-[#0b1016] border-b border-slate-800/70 p-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-start gap-1 overflow-x-auto whitespace-nowrap scrollbar-none py-1">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-mono font-medium transition-all ${
              activeTab === 'dashboard' 
                ? 'bg-slate-800 text-white border-l-2 border-emerald-500' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <TrendingUpIcon className="h-3.5 w-3.5 text-emerald-400" />
            <span>Market Liveboard</span>
          </button>
          
          <button
            onClick={() => setActiveTab('graph')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-mono font-medium transition-all ${
              activeTab === 'graph' 
                ? 'bg-slate-800 text-white border-l-2 border-teal-500' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <NetworkIcon className="h-3.5 w-3.5 text-teal-400" />
            <span>Neo4j Graph citations</span>
          </button>

          <button
            onClick={() => setActiveTab('scaffold')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-mono font-medium transition-all ${
              activeTab === 'scaffold' 
                ? 'bg-slate-800 text-white border-l-2 border-cyan-500' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <FolderIcon className="h-3.5 w-3.5 text-cyan-400" />
            <span>Python Scaffold Explorer</span>
            <span className="bg-cyan-500/10 text-[9px] px-1 py-0.2 rounded text-cyan-300">10 files</span>
          </button>

          <button
            onClick={() => setActiveTab('handbook')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-mono font-medium transition-all ${
              activeTab === 'handbook' 
                ? 'bg-slate-800 text-white border-l-2 border-purple-500' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <BookOpenIcon className="h-3.5 w-3.5 text-purple-400" />
            <span>Local Handbook</span>
          </button>
        </div>
      </div>

      {/* Main Body Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 sm:px-6 lg:px-8">
        
        <AnimatePresence mode="wait">
          
          {/* TAB 1: Live forecasting dashboard simulator */}
          {activeTab === 'dashboard' && (
            <motion.div
              key="dashboard-tab"
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-6"
            >
              {/* Left 2/3: Hypothesis listings */}
              <div className="lg:col-span-2 space-y-5">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                      <LayersIcon className="h-4.5 w-4.5 text-emerald-400" />
                      Active Scientific Hypotheses Pool
                    </h2>
                    <p className="text-xs text-slate-400">Reputational seed markers indicating estimated reproducibility probability.</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  {MOCK_HYPOTHESES.map((hyp) => {
                    const isSelected = selectedHypothesis.id === hyp.id;
                    return (
                      <div 
                        key={hyp.id} 
                        onClick={() => { setSelectedHypothesis(hyp); handleResetSimulation(); }}
                        className={`group rounded-xl border p-4 transition-all cursor-pointer ${
                          isSelected 
                            ? 'bg-slate-800/90 border-emerald-500/60 shadow-lg shadow-emerald-500/5' 
                            : 'bg-slate-900/40 border-slate-800 hover:border-slate-700/80 hover:bg-slate-900/70'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3 mb-2">
                          <span className="bg-slate-800 border border-slate-700 text-[10px] uppercase tracking-wider px-2.5 py-0.5 rounded-md font-mono text-slate-300">
                            {hyp.category}
                          </span>
                          <div className="text-right">
                            <div className="text-xs font-mono text-slate-400">Credibility Index</div>
                            <div className={`text-xl font-mono font-bold ${
                              hyp.consensusProbability > 75 ? 'text-emerald-400' : hyp.consensusProbability > 55 ? 'text-amber-400' : 'text-rose-400'
                            }`}>
                              {hyp.consensusProbability}%
                            </div>
                          </div>
                        </div>

                        <h3 className="text-sm font-semibold text-slate-100 group-hover:text-emerald-300 transition-colors mb-2 line-clamp-2">
                          {hyp.title}
                        </h3>

                        <p className="text-xs text-slate-400 mb-3 line-clamp-2 italic font-mono bg-slate-950/50 p-2 rounded border border-slate-900">
                          &ldquo;{hyp.abstract}&rdquo;
                        </p>

                        <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-400 border-t border-slate-800/80 pt-3">
                          <div className="flex items-center gap-1">
                            <UsersIcon className="h-3 w-3 text-slate-500" />
                            <span>{hyp.activeForecasters} peer experts forecasting</span>
                          </div>
                          <div>&bull;</div>
                          <div>
                            Seeds Pooled: <span className="font-mono font-medium text-slate-200">{hyp.totalPooledSeeds.toLocaleString()} seeds</span>
                          </div>
                          <div>&bull;</div>
                          <div className="truncate max-w-xs text-slate-500 font-mono">
                            {hyp.publicationRef}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Right 1/3: Forecasting engine widget (LMSR) */}
              <div className="space-y-6">
                
                {/* Seed balance header widget */}
                <div className="bg-gradient-to-br from-slate-900 to-[#101922] border border-slate-800 rounded-xl p-4">
                  <div className="flex justify-between items-center mb-3">
                    <div className="flex items-center gap-2">
                      <div className="h-7 w-7 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
                        <LeafIcon className="h-4 w-4 text-emerald-400" />
                      </div>
                      <span className="text-xs font-mono text-slate-300">Your REP-Seeds Ledger</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500">MOCK LEDGER ACCOUNT</span>
                  </div>
                  <div className="text-2xl font-mono font-bold text-white flex items-baseline gap-1">
                    {userSeedsBalance.toLocaleString()}
                    <span className="text-xs text-emerald-400">seeds</span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">Virtual reputational collateral issued for biomedical credibility pooling.</p>
                </div>

                {/* Interactive trade terminal */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                  <div className="border-b border-slate-800 pb-3">
                    <h3 className="text-xs font-mono font-bold tracking-wider text-slate-400 uppercase">Forecasting Action Terminal</h3>
                    <p className="text-[11px] text-slate-500 mt-0.5">Scored using automated Logarithmic Market Scoring Rule (LMSR) rules.</p>
                  </div>

                  {/* Active Selection Details */}
                  <div className="bg-[#0b1016] border border-slate-800 p-3 rounded-lg">
                    <span className="text-[9px] uppercase tracking-wider font-mono text-slate-500">SELECTED HYPOTHESIS REF</span>
                    <h4 className="text-xs text-slate-200 font-medium line-clamp-2 mt-1 mb-2 font-mono">
                      Ref #{selectedHypothesis.id} - {selectedHypothesis.title}
                    </h4>
                    <div className="flex items-center justify-between text-xs border-t border-slate-800/60 pt-2 font-mono">
                      <span className="text-slate-400">Initial Probability:</span>
                      <span className="text-white font-bold">{selectedHypothesis.consensusProbability}%</span>
                    </div>
                  </div>

                  {!simulatedReceipt ? (
                    <form onSubmit={handleSimulateTrade} className="space-y-4">
                      {/* Buy Pool Type Selection */}
                      <div>
                        <label className="text-xs text-slate-400 font-mono block mb-2">Predictive Decision Pool</label>
                        <div className="grid grid-cols-2 gap-2">
                          <button
                            type="button"
                            onClick={() => setPredictionSide('YES')}
                            className={`py-2 rounded-lg font-mono text-xs font-bold transition-all border ${
                              predictionSide === 'YES'
                                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500'
                                : 'bg-slate-950/60 text-slate-400 border-slate-800 hover:text-slate-200'
                            }`}
                          >
                            YES (Claims Hold Robust)
                          </button>
                          <button
                            type="button"
                            onClick={() => setPredictionSide('NO')}
                            className={`py-2 rounded-lg font-mono text-xs font-bold transition-all border ${
                              predictionSide === 'NO'
                                ? 'bg-rose-500/20 text-rose-300 border-rose-500'
                                : 'bg-slate-950/60 text-slate-400 border-slate-800 hover:text-slate-200'
                            }`}
                          >
                            NO (Findings Flawed/Fail)
                          </button>
                        </div>
                      </div>

                      {/* Buy Volume Range Slider */}
                      <div>
                        <div className="flex justify-between items-center text-xs font-mono mb-1.5">
                          <span className="text-slate-400">Position Seeds:</span>
                          <span className="text-white font-bold">{seedTradeAmount} Seeds</span>
                        </div>
                        <input
                          type="range"
                          min="50"
                          max="2000"
                          step="50"
                          value={seedTradeAmount}
                          onChange={(e) => setSeedTradeAmount(parseInt(e.target.value))}
                          className="w-full accent-emerald-500"
                        />
                        <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
                          <span>50 (Min)</span>
                          <span>2,000 (Max)</span>
                        </div>
                      </div>

                      <button
                        type="submit"
                        disabled={seedTradeAmount > userSeedsBalance}
                        className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold py-2.5 rounded-lg text-xs font-mono hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
                      >
                        Execute Credibility Pool Trade
                      </button>
                    </form>
                  ) : (
                    <motion.div 
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="bg-emerald-950/20 border border-emerald-800/30 rounded-lg p-3.5 space-y-3 font-mono"
                    >
                      <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold">
                        <CheckCircle2Icon className="h-4 w-4" />
                        <span>Position Recorded in Ledger</span>
                      </div>
                      
                      <div className="space-y-1.5 text-xs text-slate-300 border-t border-slate-800 pt-2.5">
                        <div className="flex justify-between">
                          <span className="text-slate-500">Seeds Committed:</span>
                          <span className="text-white font-bold">{seedTradeAmount} Seeds</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Mock Pool Credibility Shares Obtained:</span>
                          <span className="text-emerald-300 font-bold">{simulatedReceipt.sharesGained} Shares</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Updated Pool Credibility:</span>
                          <span className="text-white font-bold">{simulatedReceipt.newConsensus}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Slippage Applied:</span>
                          <span className="text-amber-400 font-bold">{simulatedReceipt.slippage}%</span>
                        </div>
                      </div>

                      <div className="text-[10px] bg-slate-950/80 p-2 rounded border border-slate-900 select-all truncate text-slate-400">
                        {simulatedReceipt.txHash}
                      </div>

                      <button
                        type="button"
                        onClick={handleResetSimulation}
                        className="w-full text-center bg-slate-800 hover:bg-slate-700 text-slate-100 py-1.5 rounded text-xs font-bold transition"
                      >
                        Trade Another Position
                      </button>
                    </motion.div>
                  )}

                  <div className="text-[11px] text-slate-500 p-2 rounded bg-slate-950/40 border border-slate-900/60 leading-relaxed">
                    <span className="font-semibold text-slate-400 block mb-0.5">What is this simulation?</span>
                    The LMSR algorithm computes custom token weight payouts based on scientific entropy scoring. This ensures researchers who spot flaws early extract exponential seed payouts from the pool, establishing natural credibility signals.
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* TAB 2: Neo4j Node graph citations simulated */}
          {activeTab === 'graph' && (
            <motion.div
              key="graph-tab"
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="space-y-6"
            >
              <div className="bg-[#0b1016] border border-slate-800 p-5 rounded-2xl">
                <div className="max-w-3xl mb-4">
                  <h2 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                    <NetworkIcon className="h-4.5 w-4.5 text-teal-400" />
                    Neo4j Research Co-Occurrence Network Model
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Visualizing citation loops and author institutional connections indexed dynamically through external endpoints (e.g. OpenAlex). Safe-checks node loops indicating academic collusion.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  {/* Left list details */}
                  <div className="md:col-span-1 space-y-3">
                    <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400">Node Entities</h3>
                    <div className="space-y-1">
                      {MOCK_GRAPH_NODES.map(node => (
                        <div key={node.id} className="p-2 rounded-lg bg-slate-900/80 border border-slate-800 text-xs flex justify-between items-center">
                          <span className="font-mono text-slate-300 font-medium truncate max-w-[120px]">{node.id}</span>
                          <span className={`text-[9px] px-1.5 py-0.2 rounded font-mono ${
                            node.type === 'ClinicalTrial' ? 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20' :
                            node.type === 'PolicyGuideline' ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20' :
                            node.type === 'GenomicsPaper' ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20' :
                            'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                          }`}>
                            {node.type}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Schema / Visual Mock Graph */}
                  <div className="md:col-span-2 bg-slate-950/80 border border-slate-800 rounded-xl relative overflow-hidden min-h-[350px] flex items-center justify-center p-4">
                    
                    {/* Background grid lines */}
                    <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-30"></div>

                    {/* Simulating graph visualization purely using Tailwind elements */}
                    <div className="absolute top-8 left-1/2 transform -translate-x-1/2 flex flex-col items-center">
                      <div className="h-10 w-10 rounded-full bg-indigo-600 border-2 border-slate-900 flex items-center justify-center text-[10px] font-bold shadow-lg shadow-indigo-500/20 text-white select-all">
                        R21
                      </div>
                      <span className="text-[9px] font-mono text-slate-400 mt-1">R21 Trial</span>
                    </div>

                    <div className="absolute top-28 left-8 flex flex-col items-center">
                      <div className="h-9 w-9 rounded-full bg-emerald-600 border-2 border-slate-900 flex items-center justify-center text-[10px] font-bold shadow-lg shadow-emerald-500/20 text-white">
                        Lagos
                      </div>
                      <span className="text-[9px] font-mono text-slate-400 mt-1">Lagos CRISPR</span>
                    </div>

                    <div className="absolute top-36 right-12 flex flex-col items-center">
                      <div className="h-9 w-9 rounded-full bg-amber-600 border-2 border-slate-900 flex items-center justify-center text-[10px] font-bold shadow-lg shadow-amber-500/20 text-white">
                        WHO
                      </div>
                      <span className="text-[9px] font-mono text-slate-400 mt-1">WHO Standards</span>
                    </div>

                    <div className="absolute bottom-12 left-1/3 transform -translate-x-1/2 flex flex-col items-center">
                      <div className="h-9 w-9 rounded-full bg-teal-600 border-2 border-slate-900 flex items-center justify-center text-[10px] font-bold shadow-lg shadow-teal-500/20 text-white">
                        Kigali
                      </div>
                      <span className="text-[9px] font-mono text-slate-400 mt-1">Kigali Algae</span>
                    </div>

                    <div className="absolute bottom-6 right-1/4 flex flex-col items-center">
                      <div className="h-9 w-9 rounded-full bg-rose-600 border-2 border-slate-900 flex items-center justify-center text-[10px] font-bold shadow-lg shadow-rose-500/20 text-white">
                        MDR
                      </div>
                      <span className="text-[9px] font-mono text-slate-400 mt-1">MDR TB Gen</span>
                    </div>

                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
                      <div className="h-12 w-12 rounded-full bg-slate-800 border-2 border-teal-500 flex items-center justify-center text-[10px] font-bold shadow-lg shadow-teal-500/10 text-slate-300">
                        Index
                      </div>
                      <span className="text-[9px] font-mono text-slate-500 mt-1">OpenAlex Link</span>
                    </div>

                    {/* Visual Connection Lines */}
                    <svg className="absolute inset-0 h-full w-full pointer-events-none z-0">
                      <line x1="50%" y1="15%" x2="50%" y2="50%" stroke="#334155" strokeWidth="1.5" strokeDasharray="4 2" />
                      <line x1="20%" y1="40%" x2="50%" y2="50%" stroke="#10b981" strokeWidth="1" />
                      <line x1="80%" y1="50%" x2="50%" y2="15%" stroke="#334155" strokeWidth="1" strokeDasharray="3" />
                      <line x1="33%" y1="80%" x2="50%" y2="50%" stroke="#0d9488" strokeWidth="1" />
                      <line x1="75%" y1="85%" x2="50%" y2="50%" stroke="#334155" strokeWidth="1.5" />
                      <line x1="20%" y1="40%" x2="33%" y2="80%" stroke="#0d9488" strokeWidth="1" strokeDasharray="5" />
                    </svg>

                    <div className="absolute bottom-3 left-3 bg-slate-900/90 text-[10px] px-2 py-1 rounded border border-slate-800 font-mono text-slate-400">
                      Relation Model: Neo4j Aura Graph Mapping
                    </div>
                  </div>

                  {/* Right listed relationships */}
                  <div className="md:col-span-1 space-y-3">
                    <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400">Co-citation Relationships</h3>
                    <div className="space-y-1.5 max-h-[300px] overflow-y-auto pr-1">
                      {MOCK_GRAPH_LINKS.map((link, idx) => (
                        <div key={idx} className="p-2 rounded-lg bg-slate-900/60 border border-slate-800/60 text-[10px]">
                          <div className="flex justify-between text-slate-300 font-medium font-mono mb-1">
                            <span>{link.source}</span>
                            <span className="text-slate-500">&rarr;</span>
                            <span>{link.target}</span>
                          </div>
                          <span className="bg-slate-950 font-mono text-slate-400 px-1.5 py-0.5 rounded text-[8px] tracking-wide block text-center border border-slate-900">
                            {link.relationship}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Neo4j Cypher Command Prompt Box */}
                <div className="mt-6 p-4 rounded-xl bg-slate-950/90 border border-slate-800/80 font-mono">
                  <div className="flex justify-between items-center mb-2 border-b border-slate-900 pb-2">
                    <span className="text-xs text-slate-400 font-bold flex items-center gap-1.5">
                      <TerminalIcon className="h-3.5 w-3.5 text-teal-400" />
                      Cypher Graph Query (Neo4j Engine)
                    </span>
                    <span className="text-[10px] text-slate-500">app/graph/cooccurrence.py</span>
                  </div>
                  <pre className="text-xs text-teal-300 overflow-x-auto whitespace-pre p-2 rounded bg-slate-950">
{`MATCH (p1:ResearchPaper)-[:CO_CITED]->(p2:ResearchPaper)
WHERE p1.region = 'Africa'
RETURN p1.title, p2.title, count(*) AS strength
ORDER BY strength DESC LIMIT 10`}
                  </pre>
                  <p className="text-[11px] text-slate-500 mt-2">
                    This Cypher routine identifies dense citation hubs. In clinical validation, isolated co-citation clusters receive lower credibility margins compared to widely cited heterogeneous research structures.
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* TAB 3: Code Scaffold Explorer */}
          {activeTab === 'scaffold' && (
            <motion.div
              key="scaffold-tab"
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="grid grid-cols-1 md:grid-cols-4 gap-6"
            >
              {/* Left Column: File File List tree */}
              <div className="md:col-span-1 space-y-4">
                <div className="p-3 bg-[#0b1016] border border-slate-800 rounded-xl">
                  <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-3 px-1 flex items-center justify-between">
                    <span>File Index Skeleton</span>
                    <span className="text-[10px] font-normal text-slate-500">mbhewoo-labs/</span>
                  </h3>
                  
                  <nav className="space-y-1">
                    {SCAFFOLD_FILES.map((file, idx) => {
                      const isSelected = selectedFileIdx === idx;
                      return (
                        <button
                          key={file.path}
                          onClick={() => { setSelectedFileIdx(idx); setCopiedFile(null); }}
                          className={`w-full text-left p-2.5 rounded-lg text-xs font-mono flex items-center justify-between group transition-all ${
                            isSelected 
                              ? 'bg-slate-800 text-cyan-300 font-semibold border-l-2 border-cyan-400' 
                              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                          }`}
                        >
                          <div className="flex items-center gap-2 truncate">
                            {file.path.startsWith('tests/') ? (
                              <TerminalIcon className={`h-3.5 w-3.5 ${isSelected ? 'text-amber-400' : 'text-slate-500'}`} />
                            ) : (
                              <FileCodeIcon className={`h-3.5 w-3.5 ${isSelected ? 'text-cyan-400' : 'text-slate-500'}`} />
                            )}
                            <span className="truncate">{file.label}</span>
                          </div>
                          <ChevronRightIcon className={`h-3 w-3 opacity-0 group-hover:opacity-100 transition ${
                            isSelected ? 'text-cyan-300' : 'text-slate-500'
                          }`} />
                        </button>
                      );
                    })}
                  </nav>
                </div>

                <div className="bg-slate-900 border border-slate-800/80 p-4 rounded-xl space-y-2">
                  <div className="flex items-center gap-1.5 text-xs font-mono font-medium text-slate-300">
                    <ShieldCheckIcon className="h-4 w-4 text-cyan-400" />
                    <span>Scaffold Veracity</span>
                  </div>
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    All listed files exist physically inside the docker directory tree. This allows immediate file export, Git integration, or download setups.
                  </p>
                </div>
              </div>

              {/* Right Column: Interactive Code Viewer */}
              <div className="md:col-span-3 space-y-4">
                <div className="bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden shadow-2xl flex flex-col">
                  
                  {/* File Metadata Header */}
                  <div className="bg-slate-900/90 border-b border-slate-850 px-5 py-3.5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 font-mono">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-cyan-400 font-semibold">{SCAFFOLD_FILES[selectedFileIdx].path}</span>
                        <span className="bg-slate-850 text-slate-400 border border-slate-750 px-1.5 py-0.2 rounded text-[9px]">
                          {SCAFFOLD_FILES[selectedFileIdx].lang.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 mt-0.5">{SCAFFOLD_FILES[selectedFileIdx].description}</p>
                    </div>
                    
                    <button
                      onClick={() => handleCopyCode(SCAFFOLD_FILES[selectedFileIdx].content, SCAFFOLD_FILES[selectedFileIdx].path)}
                      className="self-start sm:self-auto bg-slate-800 hover:bg-slate-750 text-slate-300 border border-slate-700 hover:text-white px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition active:scale-[0.98] cursor-pointer"
                    >
                      {copiedFile === SCAFFOLD_FILES[selectedFileIdx].path ? (
                        <>
                          <CheckIcon className="h-3.5 w-3.5 text-emerald-400" />
                          <span className="text-emerald-400">Copied!</span>
                        </>
                      ) : (
                        <>
                          <CopyIcon className="h-3.5 w-3.5" />
                          <span>Copy Code</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Code Block Container */}
                  <div className="p-5 overflow-x-auto bg-slate-950 font-mono text-xs text-slate-200 leading-relaxed max-h-[500px] overflow-y-auto">
                    <pre className="whitespace-pre select-all">
                      <code>{SCAFFOLD_FILES[selectedFileIdx].content}</code>
                    </pre>
                  </div>
                </div>

                {/* Additional directory structure list */}
                <div className="p-4 bg-slate-900/40 border border-slate-800/80 rounded-xl">
                  <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block mb-1">UNTRACKED DIRECTORIES</span>
                  <p className="text-[11px] font-mono text-slate-400">
                    The folder directories listed below were initialized with placeholder index guards (`.gitkeep` markers) to ensure structural preservation on download/export:
                  </p>
                  <ul className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-3 text-[11px] font-mono">
                    <li className="flex items-center gap-1 bg-slate-950/80 p-2 rounded border border-slate-900 text-slate-300">
                      <FolderIcon className="h-3.5 w-3.5 text-amber-500" />
                      <span>app/models/</span>
                    </li>
                    <li className="flex items-center gap-1 bg-slate-950/80 p-2 rounded border border-slate-900 text-slate-300">
                      <FolderIcon className="h-3.5 w-3.5 text-amber-500" />
                      <span>app/schemas/</span>
                    </li>
                    <li className="flex items-center gap-1 bg-slate-950/80 p-2 rounded border border-slate-900 text-slate-300">
                      <FolderIcon className="h-3.5 w-3.5 text-amber-500" />
                      <span>app/services/</span>
                    </li>
                    <li className="flex items-center gap-1 bg-slate-950/80 p-2 rounded border border-slate-900 text-slate-300">
                      <FolderIcon className="h-3.5 w-3.5 text-amber-500" />
                      <span>app/ingestion/</span>
                    </li>
                    <li className="flex items-center gap-1 bg-slate-950/80 p-2 rounded border border-slate-900 text-slate-300">
                      <FolderIcon className="h-3.5 w-3.5 text-amber-500" />
                      <span>app/markets/</span>
                    </li>
                    <li className="flex items-center gap-1 bg-slate-950/80 p-2 rounded border border-slate-900 text-slate-300">
                      <FolderIcon className="h-3.5 w-3.5 text-amber-500" />
                      <span>app/ledger/</span>
                    </li>
                    <li className="flex items-center gap-1 bg-slate-950/80 p-2 rounded border border-slate-900 text-slate-300">
                      <FolderIcon className="h-3.5 w-3.5 text-emerald-500" />
                      <span>app/graph/</span>
                    </li>
                    <li className="flex items-center gap-1 bg-slate-950/80 p-2 rounded border border-slate-900 text-slate-300">
                      <FolderIcon className="h-3.5 w-3.5 text-blue-500" />
                      <span>alembic/</span>
                    </li>
                  </ul>
                </div>
              </div>
            </motion.div>
          )}

          {/* TAB 4: Getting Started Technical Guide */}
          {activeTab === 'handbook' && (
            <motion.div
              key="handbook-tab"
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="space-y-6 max-w-4xl mx-auto"
            >
              <div className="bg-[#0b1016] border border-slate-800 p-6 rounded-2xl space-y-6">
                
                <div>
                  <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                    <BookOpenIcon className="h-5 w-5 text-purple-400" />
                    Technical Dev Handbook
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Step-by-step instructions for installing and launching the Mbhewoo Labs codebase locally in your local Anaconda environment.
                  </p>
                </div>

                {/* Grid guidelines */}
                <div className="space-y-4 text-xs">
                  
                  {/* Step 1 */}
                  <div className="flex gap-4 items-start p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
                    <div className="h-6 w-6 rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center justify-center font-mono font-bold text-purple-400">
                      1
                    </div>
                    <div className="space-y-2 flex-1">
                      <h4 className="font-bold text-slate-200">Prepare local files & Environment</h4>
                      <p className="text-slate-400 leading-relaxed">
                        Copy the template configuration `mbhewoo-labs/.env.example` into a local `.env` file. Put in your local database credential links:
                      </p>
                      <pre className="p-2.5 rounded bg-slate-950 font-mono text-[11px] overflow-x-auto text-slate-300 border border-slate-900">
{`cp .env.example .env`}
                      </pre>
                    </div>
                  </div>

                  {/* Step 2 */}
                  <div className="flex gap-4 items-start p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
                    <div className="h-6 w-6 rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center justify-center font-mono font-bold text-purple-400">
                      2
                    </div>
                    <div className="space-y-2 flex-1">
                      <h4 className="font-bold text-slate-200">Boot Conda Environment (Python 3.13)</h4>
                      <p className="text-slate-400 leading-relaxed">
                        Create and activate an environment targeted at Python 3.13:
                      </p>
                      <pre className="p-2.5 rounded bg-slate-950 font-mono text-[11px] overflow-x-auto text-slate-300 border border-slate-900">
{`conda create -n mbhewoo python=3.13 -y
conda activate mbhewoo`}
                      </pre>
                    </div>
                  </div>

                  {/* Step 3 */}
                  <div className="flex gap-4 items-start p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
                    <div className="h-6 w-6 rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center justify-center font-mono font-bold text-purple-400">
                      3
                    </div>
                    <div className="space-y-2 flex-1">
                      <h4 className="font-bold text-slate-200">pip Install Dependencies</h4>
                      <p className="text-slate-400 leading-relaxed">
                        Install tracked pip requirements including ASGI servers and modern SQLAlchemy + Neo4j drivers:
                      </p>
                      <pre className="p-2.5 rounded bg-slate-950 font-mono text-[11px] overflow-x-auto text-slate-300 border border-slate-900">
{`pip install -r requirements.txt`}
                      </pre>
                    </div>
                  </div>

                  {/* Step 4 */}
                  <div className="flex gap-4 items-start p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
                    <div className="h-6 w-6 rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center justify-center font-mono font-bold text-purple-400">
                      4
                    </div>
                    <div className="space-y-2 flex-1">
                      <h4 className="font-bold text-slate-200">Run Development Server or test suite</h4>
                      <p className="text-slate-400 leading-relaxed">
                        Launch the FastAPI development environment with autoreload enabled, or trigger pytest:
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-1">
                        <div>
                          <span className="text-[10px] text-slate-500 font-mono block mb-1">RUN APP SERVER</span>
                          <pre className="p-2 rounded bg-slate-950 font-mono text-[11px] text-slate-300 border border-slate-900">
{`uvicorn app.main:app --reload`}
                          </pre>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-500 font-mono block mb-1">TRIGGER PYTESTS</span>
                          <pre className="p-2 rounded bg-slate-950 font-mono text-[11px] text-slate-300 border border-slate-900">
{`pytest`}
                          </pre>
                        </div>
                      </div>
                    </div>
                  </div>

                </div>

                <div className="bg-purple-950/20 border border-purple-800/20 p-4 rounded-xl flex items-start gap-3">
                  <InfoIcon className="h-5 w-5 text-purple-400 flex-shrink-0 mt-0.5" />
                  <div className="text-[11px] text-slate-400 leading-relaxed">
                    <span className="font-semibold text-slate-300 block mb-1">Deployment Roadmap Tips</span>
                    For corporate cloud deployment, we recommend mounting the Gunicorn server wrapping the Uvicorn ASGI workers. Host configurations should align the SQLAlchemy session connection pool with Supabase's transaction pooling mode (typically port 6543) to avoid database execution fatigue.
                  </div>
                </div>

              </div>
            </motion.div>
          )}

        </AnimatePresence>

      </main>

      {/* Workspace Footer */}
      <footer className="border-t border-slate-800 bg-[#070b0f] py-4 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs font-mono text-slate-500">
          <p>Mbhewoo Labs MVP Scaffold Core Series. Licenced under Apache 2.0.</p>
          <div className="flex gap-4">
            <span>FastAPI 0.111.0</span>
            <span>SQLAlchemy 2.0</span>
            <span>Neo4j Agent Active</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
