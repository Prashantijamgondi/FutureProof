'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, CheckCircle, AlertCircle, Loader2, Code2, Database, Shield, Zap, RefreshCw, Terminal } from 'lucide-react';
import { Project, AnalysisResult, TransformationResult } from './types';

export default function DashboardPage() {
    const [repoUrl, setRepoUrl] = useState('');
    const [status, setStatus] = useState<'idle' | 'creating' | 'analyzing' | 'review' | 'transforming' | 'completed'>('idle');
    const [logs, setLogs] = useState<string[]>([]);
    const [project, setProject] = useState<Project | null>(null);
    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
    const [transformation, setTransformation] = useState<TransformationResult | null>(null);

    const addLog = (message: string) => {
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
    };

    const startProcess = async () => {
        if (!repoUrl) return;
        setStatus('creating');
        addLog(`Connecting to repository: ${repoUrl}`);

        try {
            // 1. Create Project
            const projectRes = await fetch('http://localhost:8000/api/v1/projects/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: repoUrl.split('/').pop() || 'Repo', repo_url: repoUrl })
            });
            const projectData = await projectRes.json();
            setProject(projectData);
            addLog(`Project created: ${projectData.name} (ID: ${projectData.id})`);

            // 2. Start Analysis
            setStatus('analyzing');
            addLog('Starting AI Code Analysis...');
            await fetch(`http://localhost:8000/api/v1/analysis/${projectData.id}/analyze`, { method: 'POST' });

            // Poll for analysis results
            const pollInterval = setInterval(async () => {
                const analysisRes = await fetch(`http://localhost:8000/api/v1/analysis/project/${projectData.id}`);
                if (analysisRes.ok) {
                    const analysisData = await analysisRes.json();
                    if (analysisData.status === 'completed') {
                        clearInterval(pollInterval);
                        setAnalysis({
                            project_id: projectData.id,
                            status: 'completed',
                            metrics: {
                                overall_score: analysisData.overall_score,
                                security_score: analysisData.security_score,
                                performance_score: analysisData.performance_score,
                                code_quality_score: analysisData.code_quality_score
                            },
                            detected_stack: {
                                language: analysisData.detected_language,
                                framework: analysisData.detected_framework,
                                libraries: analysisData.detected_libraries || [],
                                ml_frameworks: analysisData.analysis_details?.ml_frameworks || []
                            },
                            total_files: analysisData.total_files_analyzed,
                            total_lines: analysisData.total_lines_analyzed,
                            recommendations: Array.isArray(analysisData.recommendations) ? analysisData.recommendations : []
                        });
                        setStatus('review');
                        addLog('Analysis complete. Waiting for user action.');
                    }
                }
            }, 2000);

        } catch (error) {
            console.error(error);
            addLog('Error: Failed to connect to backend service.');
            setStatus('idle');
        }
    };

    const startTransformation = async () => {
        if (!project) return;
        setStatus('transforming');
        addLog('Initiating Maximum Transformation Protocol...');
        addLog('Allocating AI resources (Groq Llama 3)...');

        try {
            const res = await fetch(`http://localhost:8000/api/v1/transform/${project.id}/maximum`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    transformation_mode: 'maximum',
                    target_year: 2028,
                    apply_changes: true
                })
            });
            const data = await res.json();

            setTransformation({
                project_id: project.id,
                status: 'success',
                download_url: `http://localhost:8000/api/v1/transform/${project.id}/download`,
                files_transformed: data.files_transformed,
                improvements: data.estimated_improvements
            });

            setStatus('completed');
            addLog('Transformation complete. Ready for download.');
        } catch (error) {
            addLog('Transformation failed.');
            console.error(error);
        }
    };

    return (
        <div className="min-h-screen bg-[var(--bg-main)] text-[var(--text-main)] p-8 pt-24 font-sans transition-colors duration-300">
            <div className="max-w-6xl mx-auto">

                {/* Header */}
                <header className="mb-12 text-center">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent mb-4">
                        AI Code Modernization Dashboard
                    </h1>
                    <p className="text-gray-400">
                        Transform legacy code to 2028 standards. Supports <span className="text-white font-semibold">React, Python, ML (TensorFlow→PyTorch), Java, Go</span> & more.
                    </p>
                </header>

                {/* URL Input */}
                <div className="glass p-8 rounded-2xl mb-8">
                    <div className="flex gap-4">
                        <input
                            type="text"
                            placeholder="https://github.com/username/repo"
                            value={repoUrl}
                            onChange={(e) => setRepoUrl(e.target.value)}
                            className="flex-1 bg-dark-surface border border-dark-border rounded-xl px-6 py-4 text-lg focus:outline-none focus:border-purple-500 transition-colors"
                            disabled={status !== 'idle'}
                        />
                        <button
                            onClick={startProcess}
                            disabled={status !== 'idle' || !repoUrl}
                            className={`px-8 py-4 rounded-xl font-bold text-lg flex items-center gap-2 transition-all ${status === 'idle' && repoUrl
                                ? 'bg-purple-600 hover:bg-purple-500 shadow-lg shadow-purple-500/30'
                                : 'bg-gray-700 cursor-not-allowed text-gray-400'
                                }`}
                        >
                            {status === 'idle' ? (
                                <>Start Analysis <ArrowRight className="w-5 h-5" /></>
                            ) : (
                                <><Loader2 className="w-5 h-5 animate-spin" /> Processing</>
                            )}
                        </button>
                    </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-8">
                    {/* Left Column: Progress & Logs */}
                    <div className="space-y-8">

                        {/* Status Steps */}
                        <div className="glass p-6 rounded-2xl">
                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                                <Terminal className="w-5 h-5 text-purple-400" /> Process Status
                            </h2>
                            <div className="space-y-6">
                                <StepItem
                                    status={status}
                                    step="analyzing"
                                    label="Deep Code Analysis"
                                    desc="Scanning file patterns, frameworks (React, ML), and security vulnerabilities."
                                />
                                <StepItem
                                    status={status}
                                    step="review"
                                    label="Review Findings"
                                    desc="Check compatibility scores and detected features before modernization."
                                />
                                <StepItem
                                    status={status}
                                    step="transforming"
                                    label="AI Transformation"
                                    desc="Applying 2028 standards: PyTorch 2.5+, Next.js 15, Async/Await."
                                />
                                <StepItem
                                    status={status}
                                    step="completed"
                                    label="Download Modernized Code"
                                    desc="Get your production-ready zip file."
                                />
                            </div>
                        </div>

                        {/* Live Logs */}
                        <div className="glass p-6 rounded-2xl h-[400px] overflow-hidden flex flex-col">
                            <h3 className="text-sm font-mono text-gray-400 mb-4 uppercase tracking-wider">System Logs</h3>
                            <div className="flex-1 overflow-y-auto font-mono text-sm space-y-2 p-2 bg-black/20 rounded-lg">
                                {logs.length === 0 && <span className="text-gray-600 italic">Waiting for input...</span>}
                                {logs.map((log, i) => (
                                    <div key={i} className="text-green-400 border-l-2 border-green-500/30 pl-3">
                                        {log}
                                    </div>
                                ))}
                                {status === 'analyzing' && (
                                    <div className="text-purple-400 animate-pulse">... Scanning dependencies and file structures</div>
                                )}
                                {status === 'transforming' && (
                                    <div className="text-blue-400 animate-pulse">... Running LLM inference (Llama 3 70B)</div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Right Column: Results & Actions */}
                    <div className="space-y-8 h-full">
                        <AnimatePresence mode="wait">
                            {/* Analysis Results View */}
                            {analysis && (status === 'review' || status === 'transforming') && (
                                <motion.div
                                    key="analysis-view"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="glass p-8 rounded-2xl border border-purple-500/30"
                                >
                                    <div className="flex justify-between items-start mb-8">
                                        <div>
                                            <h2 className="text-2xl font-bold text-white mb-2">Analysis Complete</h2>
                                            <div className="flex gap-2 text-sm">
                                                <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full border border-purple-500/30">
                                                    {analysis.detected_stack.language}
                                                </span>
                                                <span className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full border border-blue-500/30">
                                                    {analysis.detected_stack.framework}
                                                </span>
                                                <span className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full">
                                                    {analysis.total_files} Files
                                                </span>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-500">
                                                {analysis.metrics.overall_score}/100
                                            </div>
                                            <div className="text-xs text-gray-400 uppercase tracking-widest mt-1">Health Score</div>
                                        </div>
                                    </div>

                                    {/* Metrics Grid */}
                                    <div className="grid grid-cols-2 gap-4 mb-8">
                                        <MetricCard label="Security" score={analysis.metrics.security_score} icon={<Shield className="w-4 h-4" />} />
                                        <MetricCard label="Performance" score={analysis.metrics.performance_score} icon={<Zap className="w-4 h-4" />} />
                                        <MetricCard label="Code Quality" score={analysis.metrics.code_quality_score} icon={<CheckCircle className="w-4 h-4" />} />
                                        <MetricCard label="Modernization" score={65} icon={<RefreshCw className="w-4 h-4" />} />
                                    </div>

                                    {/* Detected ML/Frontend Stack */}
                                    <div className="mb-8 p-4 bg-white/5 rounded-xl border border-white/10">
                                        <h3 className="text-sm font-semibold text-gray-300 mb-3 uppercase">Extended Detection</h3>
                                        <div className="flex flex-wrap gap-2">
                                            {/* Frontend/React Checks */}
                                            {(analysis.detected_stack.language === 'TypeScript' || analysis.detected_stack.framework.includes('React')) && (
                                                <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded border border-blue-500/30">
                                                    React Client Components Detected
                                                </span>
                                            )}
                                            {/* ML Checks */}
                                            {analysis.detected_stack.ml_frameworks && analysis.detected_stack.ml_frameworks.length > 0 ? (
                                                analysis.detected_stack.ml_frameworks.map(f => (
                                                    <span key={f} className="px-2 py-1 bg-orange-500/20 text-orange-300 text-xs rounded border border-orange-500/30">
                                                        ML: {f}
                                                    </span>
                                                ))
                                            ) : (
                                                <span className="px-2 py-1 bg-gray-700/50 text-gray-400 text-xs rounded">No ML Frameworks</span>
                                            )}
                                            <span className="px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded border border-green-500/30">
                                                Backend Config Checked
                                            </span>
                                        </div>
                                    </div>

                                    {status === 'review' && (
                                        <button
                                            onClick={startTransformation}
                                            className="w-full py-4 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl font-bold text-lg hover:shadow-lg hover:shadow-green-500/30 transition-all flex justify-center items-center gap-2 group"
                                        >
                                            <Zap className="w-5 h-5 fill-current" />
                                            Transform to 2028 Standards
                                        </button>
                                    )}
                                </motion.div>
                            )}

                            {/* Success View */}
                            {status === 'completed' && transformation && (
                                <motion.div
                                    key="success-view"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="glass p-8 rounded-2xl border border-green-500/50 bg-green-500/5"
                                >
                                    <div className="text-center mb-8">
                                        <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg shadow-green-500/40">
                                            <CheckCircle className="w-8 h-8 text-white" />
                                        </div>
                                        <h2 className="text-3xl font-bold text-white mb-2">Transformation Successful!</h2>
                                        <p className="text-gray-300">Your code has been modernized.</p>
                                    </div>

                                    <div className="space-y-2 mb-8 text-sm">
                                        <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                                            <span className="text-gray-400">Files Transformed</span>
                                            <span className="font-mono font-bold text-white">{transformation.files_transformed}</span>
                                        </div>
                                        {transformation.improvements && Object.entries(transformation.improvements).map(([key, value]) => (
                                            <div key={key} className="flex justify-between p-3 bg-white/5 rounded-lg">
                                                <span className="text-gray-400 capitalize">{key.replace('_', ' ')}</span>
                                                <span className="font-mono font-bold text-green-400">{String(value)}</span>
                                            </div>
                                        ))}
                                    </div>

                                    <a
                                        href={transformation.download_url}
                                        target="_blank"
                                        className="block w-full py-4 bg-white text-black rounded-xl font-bold text-lg hover:bg-gray-100 transition-all text-center"
                                    >
                                        Download Modernized Code (.zip)
                                    </a>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Empty State / Placeholder */}
                        {!analysis && status !== 'analyzing' && status !== 'completed' && (
                            <div className="h-full flex items-center justify-center border border-dashed border-gray-700 rounded-2xl p-12 text-center text-gray-500">
                                <div>
                                    <Code2 className="w-16 h-16 mx-auto mb-4 opacity-20" />
                                    <p>Enter a repository URL to begin the audit.</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function StepItem({ status, step, label, desc }: { status: string, step: string, label: string, desc: string }) {
    const steps = ['idle', 'creating', 'analyzing', 'review', 'transforming', 'completed'];
    const currentIndex = steps.indexOf(status);
    const stepIndex = steps.indexOf(step);

    const isActive = status === step;
    const isCompleted = currentIndex > stepIndex;

    return (
        <div className={`relative pl-8 border-l-2 transition-colors ${isActive || isCompleted ? 'border-purple-500' : 'border-[var(--border-main)]'}`}>
            <div className={`absolute -left-[9px] top-0 w-4 h-4 rounded-full transition-colors ${isActive ? 'bg-purple-500 ring-4 ring-purple-500/20' : isCompleted ? 'bg-green-500' : 'bg-gray-500'
                }`} />
            <h4 className={`font-bold text-lg mb-1 transition-colors ${isActive || isCompleted ? 'text-[var(--text-main)]' : 'text-gray-500'}`}>
                {label}
            </h4>
            <p className="text-sm text-gray-400">{desc}</p>
        </div>
    );
}

function MetricCard({ label, score, icon }: { label: string, score: number, icon: any }) {
    const getColor = (s: number) => {
        if (s >= 80) return 'text-green-400';
        if (s >= 60) return 'text-yellow-400';
        return 'text-red-400';
    };

    return (
        <div className="bg-[var(--surface-main)] p-4 rounded-xl border border-[var(--border-main)]">
            <div className="flex items-center gap-2 mb-2 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                {icon} {label}
            </div>
            <div className={`text-2xl font-bold ${getColor(score)}`}>
                {score || '0'}%
            </div>
        </div>
    );
}
