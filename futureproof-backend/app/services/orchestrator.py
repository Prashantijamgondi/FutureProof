# from sqlalchemy.orm import Session
# from typing import Dict, Any, List
# import asyncio
# import logging
# from datetime import datetime

# from app.models.project import Project, ProjectStatus
# from app.models.analysis import Analysis
# from app.models.agent_task import AgentTask, AgentType, TaskStatus
# from app.services.cline_service import ClineService
# from app.services.kestra_service import KestraService
# from app.services.groq_service import GroqService
# from app.services.github_service import GitHubService
# from app.services.coderabbit_service import CodeRabbitService
# from app.services.oumi_service import OumiService
# from app.agents import SecurityAgent, PerformanceAgent, ArchitectureAgent, DependencyAgent
# from app.utils.code_parser import CodeParser
# from app.utils.git_operations import GitOperations

# logger = logging.getLogger(__name__)

# class OrchestratorService:
#     """Main orchestrator for multi-agent code analysis"""
    
#     def __init__(self, db: Session):
#         self.db = db
#         self.cline = ClineService()
#         self.kestra = KestraService()
#         self.groq = GroqService()
#         self.github = GitHubService()
#         self.coderabbit = CodeRabbitService()
#         self.oumi = OumiService()
        
#         # Initialize agents
#         self.agents = {
#             AgentType.SECURITY: SecurityAgent(),
#             AgentType.PERFORMANCE: PerformanceAgent(),
#             AgentType.ARCHITECTURE: ArchitectureAgent(),
#             AgentType.DEPENDENCY: DependencyAgent()
#         }
    
#     async def start_analysis(self, project_id: int):
#         """Main entry point - orchestrate entire analysis pipeline"""
#         try:
#             logger.info(f"Starting analysis for project {project_id}")
            
#             # Get project
#             project = self.db.query(Project).filter(Project.id == project_id).first()
#             if not project:
#                 raise Exception(f"Project {project_id} not found")
            
#             # Update status
#             project.status = ProjectStatus.ANALYZING
#             self.db.commit()
            
#             # Step 1: Clone and prepare repository
#             repo_path = await self._prepare_repository(project)
            
#             # Step 2: Extract code using Cline CLI
#             code_data = await self._extract_code_data(project, repo_path)
            
#             # Step 3: Run multi-agent analysis in parallel
#             agent_results = await self._run_multi_agent_analysis(project, code_data)
            
#             # Step 4: Run Kestra decision workflow
#             decision = await self._make_decision(project, agent_results)
            
#             # Step 5: Generate modernization plan with Groq
#             modernization_plan = await self._generate_modernization_plan(project, agent_results)
            
#             # Step 6: Create analysis record
#             analysis = await self._save_analysis_results(
#                 project, 
#                 agent_results, 
#                 decision, 
#                 modernization_plan
#             )
            
#             # Step 7: Fine-tune Oumi model (for Iron Intelligence Award)
#             await self._fine_tune_oumi_model(project, code_data, analysis)
            
#             # Step 8: Generate PR with recommendations (CodeRabbit integration)
#             await self._create_improvement_pr(project, analysis)
            
#             # Update project status
#             project.status = ProjectStatus.COMPLETED
#             project.completed_at = datetime.utcnow()
#             self.db.commit()
            
#             logger.info(f"Analysis completed for project {project_id}")
            
#         except Exception as e:
#             logger.error(f"Analysis failed for project {project_id}: {str(e)}")
#             project.status = ProjectStatus.FAILED
#             project.error_message = str(e)
#             self.db.commit()
    
#     async def _prepare_repository(self, project: Project) -> str:
#         """Clone repository and prepare for analysis"""
#         try:
#             import tempfile
#             import os
            
#             # Create temp directory
#             temp_dir = tempfile.mkdtemp(prefix=f"futureproof_{project.id}_")
#             repo_path = os.path.join(temp_dir, "repo")
            
#             # Clone repository
#             logger.info(f"Cloning repository: {project.repo_url}")
#             success = await self.github.clone_repository(project.repo_url, repo_path)
            
#             if not success:
#                 raise Exception("Failed to clone repository")
            
#             # Update project with repo path
#             project.repo_path = repo_path
#             self.db.commit()
            
#             logger.info(f"Repository prepared at: {repo_path}")
#             return repo_path
            
#         except Exception as e:
#             logger.error(f"Repository preparation failed: {str(e)}")
#             raise
    
#     async def _extract_code_data(self, project: Project, repo_path: str) -> Dict[str, Any]:
#         """Extract code data using Cline CLI"""
#         try:
#             logger.info("Extracting code data with Cline CLI")
            
#             # Get code structure
#             structure = await self.cline.extract_code_structure(repo_path)
            
#             # Update project metadata
#             project.total_files = structure.get("total_files", 0)
#             project.total_lines = structure.get("total_lines", 0)
#             self.db.commit()
            
#             # Parse code files
#             parser = CodeParser()
#             files = await parser.parse_directory(repo_path)
            
#             # Detect language and framework
#             detected = parser.detect_tech_stack(files)
#             project.language = detected.get("language")
#             project.framework = detected.get("framework")
#             self.db.commit()
            
#             return {
#                 "repo_path": repo_path,
#                 "files": files,
#                 "structure": structure,
#                 "language": project.language,
#                 "framework": project.framework,
#                 "total_files": project.total_files,
#                 "total_lines": project.total_lines
#             }
            
#         except Exception as e:
#             logger.error(f"Code extraction failed: {str(e)}")
#             raise
    
#     async def _run_multi_agent_analysis(
#         self, 
#         project: Project, 
#         code_data: Dict[str, Any]
#     ) -> List[Dict[str, Any]]:
#         """Run all agents in parallel"""
#         try:
#             logger.info(f"Running multi-agent analysis with {len(self.agents)} agents")
            
#             # Create agent tasks in database
#             tasks = []
#             for agent_type in self.agents.keys():
#                 task = AgentTask(
#                     project_id=project.id,
#                     agent_type=agent_type,
#                     status=TaskStatus.PENDING,
#                     input_data={"file_count": code_data.get("total_files", 0)}
#                 )
#                 self.db.add(task)
#                 tasks.append(task)
            
#             self.db.commit()
            
#             # Run agents in parallel
#             agent_coroutines = []
#             for agent_type, agent in self.agents.items():
#                 agent_coroutines.append(
#                     self._run_single_agent(agent_type, agent, code_data, tasks)
#                 )
            
#             results = await asyncio.gather(*agent_coroutines, return_exceptions=True)
            
#             # Filter out exceptions
#             valid_results = [r for r in results if not isinstance(r, Exception)]
            
#             logger.info(f"Completed {len(valid_results)}/{len(self.agents)} agent analyses")
            
#             return valid_results
            
#         except Exception as e:
#             logger.error(f"Multi-agent analysis failed: {str(e)}")
#             raise
    
#     async def _run_single_agent(
#         self,
#         agent_type: AgentType,
#         agent: Any,
#         code_data: Dict[str, Any],
#         tasks: List[AgentTask]
#     ) -> Dict[str, Any]:
#         """Run a single agent and update its task"""
#         try:
#             # Find corresponding task
#             task = next((t for t in tasks if t.agent_type == agent_type), None)
#             if task:
#                 task.status = TaskStatus.RUNNING
#                 task.started_at = datetime.utcnow()
#                 self.db.commit()
            
#             # Run agent
#             logger.info(f"Starting {agent_type} agent")
#             result = await agent.run(code_data)
            
#             # Update task
#             if task:
#                 task.status = TaskStatus.COMPLETED
#                 task.completed_at = datetime.utcnow()
#                 task.output_data = result
#                 self.db.commit()
            
#             result["agent_type"] = agent_type
#             return result
            
#         except Exception as e:
#             logger.error(f"{agent_type} agent failed: {str(e)}")
            
#             if task:
#                 task.status = TaskStatus.FAILED
#                 task.error_message = str(e)
#                 self.db.commit()
            
#             raise
    
#     async def _make_decision(
#         self,
#         project: Project,
#         agent_results: List[Dict[str, Any]]
#     ) -> Dict[str, Any]:
#         """Use Kestra + Groq AI to make decision"""
#         try:
#             logger.info("Running decision-making workflow")
            
#             # Option 1: Use Kestra workflow
#             # decision = await self.kestra.run_decision_workflow(project.id, agent_results)
            
#             # Option 2: Use Groq AI directly (faster for hackathon)
#             decision = await self.groq.make_decision(agent_results)
            
#             logger.info(f"Decision: {decision.get('decision')} (confidence: {decision.get('confidence', 0):.2f})")
            
#             return decision
            
#         except Exception as e:
#             logger.error(f"Decision making failed: {str(e)}")
#             return {
#                 "decision": "NEEDS_REVIEW",
#                 "reasoning": f"Error in decision process: {str(e)}",
#                 "confidence": 0.0
#             }
    
#     async def _generate_modernization_plan(
#         self,
#         project: Project,
#         agent_results: List[Dict[str, Any]]
#     ) -> Dict[str, Any]:
#         """Generate modernization roadmap using Groq AI"""
#         try:
#             logger.info("Generating modernization plan")
            
#             # Prepare project info
#             project_info = {
#                 "language": project.language,
#                 "framework": project.framework,
#                 "total_files": project.total_files,
#                 "total_lines": project.total_lines
#             }
            
#             # Aggregate analysis results
#             analysis_summary = {
#                 "security_score": agent_results[0].get("score", 0) if len(agent_results) > 0 else 0,
#                 "performance_score": agent_results[1].get("score", 0) if len(agent_results) > 1 else 0,
#                 "architecture_score": agent_results[2].get("score", 0) if len(agent_results) > 2 else 0,
#                 "dependency_score": agent_results[3].get("score", 0) if len(agent_results) > 3 else 0,
#                 "critical_issues": self._extract_critical_issues(agent_results)
#             }
            
#             # Generate plan with AI
#             plan = await self.groq.generate_modernization_plan(project_info, analysis_summary)
            
#             return plan
            
#         except Exception as e:
#             logger.error(f"Modernization plan generation failed: {str(e)}")
#             return {}
    
#     async def _save_analysis_results(
#         self,
#         project: Project,
#         agent_results: List[Dict[str, Any]],
#         decision: Dict[str, Any],
#         modernization_plan: Dict[str, Any]
#     ) -> Analysis:
#         """Save analysis results to database"""
#         try:
#             # Extract scores and issues from agent results
#             security_result = next((r for r in agent_results if r.get("agent_type") == AgentType.SECURITY), {})
#             performance_result = next((r for r in agent_results if r.get("agent_type") == AgentType.PERFORMANCE), {})
#             architecture_result = next((r for r in agent_results if r.get("agent_type") == AgentType.ARCHITECTURE), {})
#             dependency_result = next((r for r in agent_results if r.get("agent_type") == AgentType.DEPENDENCY), {})
            
#             # Calculate overall score
#             scores = [
#                 security_result.get("score", 0),
#                 performance_result.get("score", 0),
#                 architecture_result.get("score", 0),
#                 dependency_result.get("score", 0)
#             ]
#             overall_score = sum(scores) / len(scores) if scores else 0
            
#             # Create analysis record
#             analysis = Analysis(
#                 project_id=project.id,
#                 security_score=security_result.get("score", 0),
#                 performance_score=performance_result.get("score", 0),
#                 architecture_score=architecture_result.get("score", 0),
#                 dependency_score=dependency_result.get("score", 0),
#                 overall_score=overall_score,
#                 security_issues=security_result.get("findings", []),
#                 performance_issues=performance_result.get("findings", []),
#                 architecture_issues=architecture_result.get("findings", []),
#                 dependency_issues=dependency_result.get("findings", []),
#                 recommendations=self._aggregate_recommendations(agent_results),
#                 modernization_roadmap=modernization_plan.get("priority_actions", []),
#                 decision=decision.get("decision"),
#                 decision_reasoning=decision.get("reasoning"),
#                 completed_at=datetime.utcnow()
#             )
            
#             self.db.add(analysis)
#             self.db.commit()
#             self.db.refresh(analysis)
            
#             logger.info(f"Analysis saved: ID {analysis.id}, Overall Score: {overall_score:.2f}")
            
#             return analysis
            
#         except Exception as e:
#             logger.error(f"Failed to save analysis: {str(e)}")
#             raise
    
#     async def _fine_tune_oumi_model(
#         self,
#         project: Project,
#         code_data: Dict[str, Any],
#         analysis: Analysis
#     ):
#         """Fine-tune Oumi model on project patterns (Iron Intelligence Award requirement)"""
#         try:
#             logger.info("Starting Oumi model fine-tuning")
            
#             # Prepare training data from analysis
#             training_data = self._prepare_training_data(code_data, analysis)
            
#             # Fine-tune model
#             result = await self.oumi.fine_tune_model(
#                 training_data=training_data,
#                 model_name=f"futureproof-project-{project.id}"
#             )
            
#             # Store fine-tuning results
#             analysis.oumi_suggestions = result
#             self.db.commit()
            
#             logger.info(f"Oumi fine-tuning completed: {result.get('status')}")
            
#         except Exception as e:
#             logger.error(f"Oumi fine-tuning failed: {str(e)}")
    
#     async def _create_improvement_pr(self, project: Project, analysis: Analysis):
#         """Create PR with improvement suggestions (CodeRabbit integration)"""
#         try:
#             logger.info("Creating improvement PR with CodeRabbit")
            
#             # Format recommendations as PR comments
#             comments = []
#             for issue in analysis.security_issues[:5]:  # Top 5 issues
#                 comments.append({
#                     "file": issue.get("file_path"),
#                     "line": issue.get("line_number"),
#                     "body": f"**{issue.get('title')}**\n\n{issue.get('description')}\n\n💡 {issue.get('suggestion')}"
#                 })
            
#             # Submit to CodeRabbit (simplified - actual implementation would create PR first)
#             # In production: Create branch, commit fixes, create PR, then add comments
#             logger.info(f"Would create PR with {len(comments)} improvement suggestions")
            
#         except Exception as e:
#             logger.error(f"PR creation failed: {str(e)}")
    
#     def _extract_critical_issues(self, agent_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """Extract critical issues from all agents"""
#         critical = []
        
#         for result in agent_results:
#             findings = result.get("findings", [])
#             critical.extend([f for f in findings if f.get("severity") == "critical"])
        
#         return critical[:10]  # Top 10 critical issues
    
#     def _aggregate_recommendations(self, agent_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """Aggregate recommendations from all agents"""
#         all_recommendations = []
        
#         for result in agent_results:
#             agent_type = result.get("agent_type", "unknown")
#             recommendations = result.get("recommendations", [])
            
#             for rec in recommendations:
#                 all_recommendations.append({
#                     "category": str(agent_type),
#                     "recommendation": rec,
#                     "priority": "high" if any(i.get("severity") == "critical" for i in result.get("findings", [])) else "medium"
#                 })
        
#         return all_recommendations
    
#     def _prepare_training_data(
#         self,
#         code_data: Dict[str, Any],
#         analysis: Analysis
#     ) -> List[Dict[str, Any]]:
#         """Prepare training data for Oumi fine-tuning"""
#         training_data = []
        
#         # Create examples from issues and fixes
#         for issue in analysis.security_issues[:20]:
#             training_data.append({
#                 "input": f"Analyze this code for security: {issue.get('code_snippet', '')}",
#                 "output": issue.get("suggestion", "")
#             })
        
#         return training_data
import os
import tempfile
import shutil
from typing import Dict, Any, List
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectStatus
from app.models.analysis import Analysis
from app.models.agent_task import AgentTask
from app.services.github_service import GitHubService
from app.services.cline_service import ClineService
from app.services.groq_service import GroqService
from app.services.oumi_service import OumiService
from app.services.coderabbit_service import CodeRabbitService
from app.agents.security_agent import SecurityAgent
from app.agents.performance_agent import PerformanceAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.dependency_agent import DependencyAgent
from app.utils.code_parser import CodeParser
from app.database import async_session_maker

logger = logging.getLogger(__name__)


class OrchestratorService:
    """
    Main orchestrator that coordinates all services and agents
    """
    
    def __init__(self, db: Session = None):
        """Initialize orchestrator with all services"""
        self.db = db
        self.github_service = GitHubService()
        self.cline_service = ClineService()
        self.groq_service = GroqService()
        self.oumi_service = OumiService()
        self.coderabbit_service = CodeRabbitService()
        
        # Initialize agents
        self.agents = {
            "security": SecurityAgent(),
            "performance": PerformanceAgent(),
            "architecture": ArchitectureAgent(),
            "dependency": DependencyAgent()
        }
    
    async def start_analysis(self, project_id: int):
        """
        Main orchestration method that runs the entire analysis pipeline
        """
        # Create a new database session for background task
        db = async_session_maker()
        
        try:
            start_time = datetime.utcnow()
            logger.info(f"Starting analysis for project {project_id}")
            
            # Get project
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                logger.error(f"Project {project_id} not found")
                return
            
            # Update status
            project.status = ProjectStatus.CLONING
            db.commit()
            
            # Step 1: Clone repository
            repo_path = await self._clone_repository(project)
            
            # Step 2: Extract code structure
            project.status = ProjectStatus.ANALYZING
            db.commit()
            
            code_data = await self._extract_code_data(repo_path, project, db)
            
            # Step 3: Run multi-agent analysis
            agent_results = await self._run_agent_analysis(project_id, code_data, db)
            
            # Step 4: Decision-making workflow
            decision = await self._make_decision(code_data, agent_results)
            
            # Step 5: Generate modernization plan
            modernization_plan = await self._generate_modernization_plan(code_data, agent_results)
            
            # Step 6: Save analysis results
            analysis = await self._save_analysis(
                project_id, 
                agent_results, 
                decision, 
                modernization_plan,
                start_time,
                db
            )
            
            # Step 7: Fine-tune Oumi model
            await self._finetune_oumi(project_id, code_data, agent_results, db)
            
            # Step 8: Create improvement PR
            await self._create_improvement_pr(project, analysis, db)
            
            # Update project status
            project.status = ProjectStatus.COMPLETED
            db.commit()
            
            # Cleanup
            self._cleanup_temp_files(repo_path)
            
            logger.info(f"Analysis completed for project {project_id}")
            
        except Exception as e:
            logger.error(f"Analysis failed for project {project_id}: {str(e)}")
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = ProjectStatus.FAILED
                db.commit()
        finally:
            db.close()
    
    async def _clone_repository(self, project: Project) -> str:
        """Clone the GitHub repository"""
        logger.info(f"Cloning repository: {project.repo_url}")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix=f"futureproof_{project.id}_")
        repo_path = os.path.join(temp_dir, "repo")
        
        # Clone repo
        success = await self.github_service.clone_repository(
            project.repo_url, 
            repo_path
        )
        
        if not success:
            raise Exception(f"Failed to clone repository: {project.repo_url}")
        
        logger.info(f"Repository prepared at: {repo_path}")
        return repo_path
    
    async def _extract_code_data(self, repo_path: str, project: Project, db: Session) -> Dict[str, Any]:
        """Extract code structure and metadata"""
        logger.info("Extracting code data with Cline CLI")
        
        # Try Cline CLI first
        code_data = await self.cline_service.extract_structure(repo_path)
        
        # Fallback to basic parser if Cline fails
        if not code_data or code_data.get("total_files", 0) == 0:
            parser = CodeParser()
            code_data = parser.parse_directory(repo_path)
        
        # Update project with extracted data
        project.total_files = code_data.get("total_files", 0)
        project.total_lines = code_data.get("total_lines", 0)
        db.commit()
        
        return code_data
    
    async def _run_agent_analysis(
        self, 
        project_id: int, 
        code_data: Dict[str, Any],
        db: Session
    ) -> List[Dict[str, Any]]:
        """Run all agents in parallel"""
        logger.info(f"Running multi-agent analysis with {len(self.agents)} agents")
        
        results = []
        
        for agent_type, agent in self.agents.items():
            logger.info(f"Starting {agent_type} agent")
            
            # Create agent task
            task = AgentTask(
                project_id=project_id,
                agent_type=agent_type,
                status="running"
            )
            db.add(task)
            db.commit()
            
            try:
                # Run agent analysis
                result = await agent.analyze(code_data)
                
                # Update task
                task.status = "completed"
                task.output_data = result
                task.completed_at = datetime.utcnow()
                db.commit()
                
                results.append({
                    "agent": agent_type,
                    "score": result.get("score", 0),
                    "findings": result.get("findings", []),
                    "recommendations": result.get("recommendations", [])
                })
                
            except Exception as e:
                logger.error(f"Agent {agent_type} failed: {str(e)}")
                task.status = "failed"
                task.error_message = str(e)
                db.commit()
        
        logger.info(f"Completed {len(results)}/{len(self.agents)} agent analyses")
        return results
    
    async def _make_decision(
        self, 
        code_data: Dict[str, Any], 
        agent_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use Groq AI to make final decision"""
        logger.info("Running decision-making workflow")
        
        try:
            decision = await self.groq_service.make_decision(code_data, agent_results)
            return decision
        except Exception as e:
            logger.error(f"Decision making failed: {str(e)}")
            return {
                "decision": "NEEDS_REVIEW",
                "reasoning": f"Error in decision making: {str(e)}",
                "confidence": 0.0
            }
    
    async def _generate_modernization_plan(
        self, 
        code_data: Dict[str, Any], 
        agent_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate modernization roadmap"""
        logger.info("Generating modernization plan")
        
        try:
            plan = await self.groq_service.generate_modernization_plan(
                code_data, 
                agent_results
            )
            return plan
        except Exception as e:
            logger.error(f"Modernization plan generation failed: {str(e)}")
            return {
                "priority_actions": [],
                "short_term_goals": [],
                "long_term_vision": []
            }
    
    async def _save_analysis(
        self,
        project_id: int,
        agent_results: List[Dict[str, Any]],
        decision: Dict[str, Any],
        modernization_plan: Dict[str, Any],
        start_time: datetime,
        db: Session
    ) -> Analysis:
        """Save analysis results to database"""
        
        # Calculate scores
        avg_scores = {}
        all_findings = {}
        all_recommendations = []
        
        for result in agent_results:
            agent_type = result["agent"]
            avg_scores[agent_type] = result.get("score", 0)
            all_findings[agent_type] = result.get("findings", [])
            all_recommendations.extend(result.get("recommendations", []))
        
        overall_score = sum(avg_scores.values()) / len(avg_scores) if avg_scores else 0
        
        # Ensure modernization_plan is a dict
        if not isinstance(modernization_plan, dict):
            modernization_plan = {
                "priority_actions": [],
                "short_term_goals": [],
                "long_term_vision": []
            }
        
        # Create analysis record
        analysis = Analysis(
            project_id=project_id,
            security_score=avg_scores.get("security", 0),
            performance_score=avg_scores.get("performance", 0),
            architecture_score=avg_scores.get("architecture", 0),
            dependency_score=avg_scores.get("dependency", 0),
            overall_score=overall_score,
            security_issues=all_findings.get("security", []),
            performance_issues=all_findings.get("performance", []),
            architecture_issues=all_findings.get("architecture", []),
            dependency_issues=all_findings.get("dependency", []),
            recommendations=all_recommendations,
            modernization_roadmap=modernization_plan if isinstance(modernization_plan, dict) else {},
            decision=decision.get("decision", "NEEDS_REVIEW"),
            decision_reasoning=decision.get("reasoning", ""),
            completed_at=datetime.utcnow(),
            processing_time_seconds=(datetime.utcnow() - start_time).total_seconds()
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        logger.info(f"Analysis saved: ID {analysis.id}, Overall Score: {overall_score:.2f}")
        return analysis
    
    async def _finetune_oumi(
        self,
        project_id: int,
        code_data: Dict[str, Any],
        agent_results: List[Dict[str, Any]],
        db: Session
    ):
        """Fine-tune Oumi model with analysis results"""
        logger.info("Starting Oumi model fine-tuning")
        
        try:
            # Prepare training data
            training_examples = self._prepare_training_data(code_data, agent_results)
            
            # Run fine-tuning
            result = await self.oumi_service.finetune(training_examples)
            
            logger.info(f"Oumi fine-tuning completed: {result.get('status')}")
            
        except Exception as e:
            logger.error(f"Oumi fine-tuning failed: {str(e)}")
    
    async def _create_improvement_pr(
        self,
        project: Project,
        analysis: Analysis,
        db: Session
    ):
        """Create PR with improvement suggestions using CodeRabbit"""
        logger.info("Creating improvement PR with CodeRabbit")
        
        try:
            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(analysis)
            
            if not suggestions:
                logger.info("No improvements to suggest")
                return
            
            # Create PR (placeholder - implement actual PR creation)
            logger.info(f"Would create PR with {len(suggestions)} improvement suggestions")
            
        except Exception as e:
            logger.error(f"PR creation failed: {str(e)}")
    
    def _prepare_training_data(
        self, 
        code_data: Dict[str, Any], 
        agent_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prepare training examples for Oumi"""
        examples = []
        
        for result in agent_results:
            for finding in result.get("findings", []):
                examples.append({
                    "input": finding.get("description", ""),
                    "output": finding.get("suggestion", ""),
                    "metadata": {
                        "agent": result["agent"],
                        "severity": finding.get("severity", "low")
                    }
                })
        
        return examples
    
    def _generate_improvement_suggestions(self, analysis: Analysis) -> List[Dict[str, Any]]:
        """Generate improvement suggestions from analysis"""
        suggestions = []
        
        # Add high-severity issues
        for issue in analysis.security_issues:
            if issue.get("severity") == "high":
                suggestions.append({
                    "type": "security",
                    "title": issue.get("title"),
                    "description": issue.get("description"),
                    "suggestion": issue.get("suggestion")
                })
        
        return suggestions
    
    def _cleanup_temp_files(self, repo_path: str):
        """Clean up temporary repository files"""
        try:
            temp_dir = os.path.dirname(repo_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temp directory: {temp_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {str(e)}")
