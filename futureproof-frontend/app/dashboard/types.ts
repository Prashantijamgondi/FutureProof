export interface Project {
    id: number;
    name: string;
    repo_url: string;
    status: 'pending' | 'analyzing' | 'analyzed' | 'transforming' | 'transformed' | 'failed';
    created_at: string;
}

export interface AnalysisMetrics {
    overall_score: number;
    security_score: number;
    performance_score: number;
    code_quality_score: number;
    maintainability_score?: number;
}

export interface DetectedStack {
    language: string;
    framework: string;
    libraries: string[];
    ml_frameworks?: string[];
}

export interface AnalysisResult {
    project_id: number;
    status: string;
    metrics: AnalysisMetrics;
    detected_stack: DetectedStack;
    total_files: number;
    total_lines: number;
    recommendations: string[];
    analysis_details?: {
        files_by_type?: Record<string, number>;
        issues_by_severity?: Record<string, number>;
    };
}

export interface TransformationResult {
    project_id: number;
    status: string;
    download_url?: string;
    files_transformed: number;
    improvements: Record<string, string>;
    migration_path?: string;
    preview_logs?: string[];
}
