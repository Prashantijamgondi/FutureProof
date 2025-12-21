# from groq import Groq
# from typing import Dict, Any, List, Optional
# import logging
# from app.config import settings
# import json

# logger = logging.getLogger(__name__)

# class GroqService:
#     """Service for Groq AI integration"""
    
#     def __init__(self):
#         self.client = Groq(api_key=settings.GROQ_API_KEY)
#         self.model = "llama-3.1-70b-versatile"  # Fast and capable
    
#     async def analyze_code_with_ai(
#         self,
#         code_snippet: str,
#         analysis_type: str,
#         context: Optional[str] = None
#     ) -> Dict[str, Any]:
#         """Use Groq AI to analyze code"""
#         try:
#             prompt = self._build_analysis_prompt(code_snippet, analysis_type, context)
            
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are an expert code analyzer. Provide detailed, actionable insights."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=0.3,
#                 max_tokens=2000
#             )
            
#             result = response.choices[0].message.content
            
#             # Try to parse JSON response
#             try:
#                 parsed_result = json.loads(result)
#                 return parsed_result
#             except json.JSONDecodeError:
#                 return {"analysis": result}
                
#         except Exception as e:
#             logger.error(f"Groq analysis failed: {str(e)}")
#             return {"error": str(e)}
    
#     async def generate_modernization_plan(
#         self,
#         project_info: Dict[str, Any],
#         analysis_results: Dict[str, Any]
#     ) -> Dict[str, Any]:
#         """Generate a modernization roadmap using AI"""
#         try:
#             prompt = f"""
#             Analyze this legacy codebase and create a detailed modernization plan:
            
#             Project Info:
#             - Language: {project_info.get('language')}
#             - Framework: {project_info.get('framework')}
#             - Total Files: {project_info.get('total_files')}
#             - Total Lines: {project_info.get('total_lines')}
            
#             Analysis Scores:
#             - Security: {analysis_results.get('security_score', 0)}/100
#             - Performance: {analysis_results.get('performance_score', 0)}/100
#             - Architecture: {analysis_results.get('architecture_score', 0)}/100
#             - Dependencies: {analysis_results.get('dependency_score', 0)}/100
            
#             Key Issues:
#             {json.dumps(analysis_results.get('critical_issues', [])[:5], indent=2)}
            
#             Generate a JSON response with:
#             1. priority_actions (list of immediate fixes)
#             2. short_term_goals (1-3 months)
#             3. long_term_vision (6-12 months)
#             4. estimated_effort (hours)
#             5. recommended_technologies (list)
#             """
            
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a software modernization expert. Create actionable, realistic plans."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=0.5,
#                 max_tokens=3000
#             )
            
#             result = response.choices[0].message.content
            
#             try:
#                 return json.loads(result)
#             except:
#                 return {"raw_plan": result}
                
#         except Exception as e:
#             logger.error(f"Modernization plan generation failed: {str(e)}")
#             return {"error": str(e)}
    
#     async def make_decision(
#         self,
#         agent_results: List[Dict[str, Any]]
#     ) -> Dict[str, Any]:
#         """AI-powered decision making based on agent results"""
#         try:
#             prompt = f"""
#             You are a technical decision-maker. Analyze these agent findings and make a decision:
            
#             Agent Results:
#             {json.dumps(agent_results, indent=2)}
            
#             Provide a JSON response with:
#             1. decision: "APPROVE" | "NEEDS_WORK" | "CRITICAL_ISSUES"
#             2. reasoning: detailed explanation
#             3. confidence: 0.0 to 1.0
#             4. next_steps: list of recommended actions
#             """
            
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a senior technical architect making code review decisions."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=0.2,
#                 max_tokens=1500
#             )
            
#             result = response.choices[0].message.content
#             return json.loads(result)
            
#         except Exception as e:
#             logger.error(f"AI decision making failed: {str(e)}")
#             return {
#                 "decision": "NEEDS_REVIEW",
#                 "reasoning": f"Error in AI analysis: {str(e)}",
#                 "confidence": 0.0
#             }
    
#     def _build_analysis_prompt(
#         self,
#         code: str,
#         analysis_type: str,
#         context: Optional[str]
#     ) -> str:
#         """Build prompt for code analysis"""
#         prompts = {
#             "security": f"Analyze this code for security vulnerabilities:\n\n{code}\n\nProvide JSON with: vulnerabilities (list), severity, recommendations",
#             "performance": f"Analyze this code for performance issues:\n\n{code}\n\nProvide JSON with: bottlenecks (list), optimizations, expected_improvement",
#             "architecture": f"Review this code architecture:\n\n{code}\n\nProvide JSON with: patterns_used, issues, improvements",
#             "quality": f"Assess code quality:\n\n{code}\n\nProvide JSON with: quality_score, issues, best_practices"
#         }
        
#         base_prompt = prompts.get(analysis_type, f"Analyze this code:\n\n{code}")
        
#         if context:
#             base_prompt += f"\n\nContext: {context}"
        
#         return base_prompt

import os
import json
from typing import Dict, Any, List
from groq import Groq
import logging

logger = logging.getLogger(__name__)


class GroqService:
    """Service for Groq AI API integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required")
        
        self.client = Groq(api_key=self.api_key)
        # Updated to currently supported model
        self.model = "llama-3.3-70b-versatile"  # ← CHANGED THIS LINE
        
    async def make_decision(
        self,
        project_data: Dict[str, Any],
        agent_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use Groq AI to make a decision based on agent analysis results
        """
        try:
            # Calculate average score
            scores = [r.get("score", 0) for r in agent_results]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            # Count critical issues
            critical_issues = sum(
                len([i for i in r.get("findings", []) if i.get("severity") == "critical"])
                for r in agent_results
            )
            
            # Create prompt
            prompt = self._create_decision_prompt(project_data, agent_results, avg_score, critical_issues)
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code analysis AI that makes decisions about code modernization projects."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse response
            decision_text = response.choices[0].message.content
            
            # Extract decision and reasoning
            decision = self._parse_decision(decision_text, avg_score, critical_issues)
            
            logger.info(f"AI decision made: {decision['decision']}")
            return decision
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return {
                "decision": "NEEDS_REVIEW",
                "reasoning": f"Error in AI analysis: {str(e)}",
                "confidence": 0.0
            }
    
    async def generate_modernization_plan(
        self,
        project_data: Dict[str, Any],
        agent_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a modernization roadmap using Groq AI"""
        try:
            prompt = self._create_modernization_prompt(project_data, agent_results)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software architect specializing in legacy code modernization."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            plan_text = response.choices[0].message.content
            plan = self._parse_modernization_plan(plan_text)
            
            logger.info("Modernization plan generated successfully")
            return plan
            
        except Exception as e:
            logger.error(f"Error generating modernization plan: {str(e)}")
            return {
                "priority_actions": ["Fix critical security issues"],
                "short_term_goals": ["Update dependencies"],
                "long_term_vision": ["Complete code modernization"]
            }
    
    def _create_decision_prompt(
        self,
        project_data: Dict[str, Any],
        agent_results: List[Dict[str, Any]],
        avg_score: float,
        critical_issues: int
    ) -> str:
        """Create a prompt for decision making"""
        return f"""
Analyze this codebase and make a modernization decision:

Project: {project_data.get('name', 'Unknown')}
Language: {project_data.get('language', 'Unknown')}
Files: {project_data.get('total_files', 0)}
Lines of Code: {project_data.get('total_lines', 0)}

Analysis Results:
- Average Score: {avg_score:.2f}/100
- Critical Issues: {critical_issues}

Agent Findings:
{json.dumps(agent_results, indent=2)}

Based on this analysis, make one of these decisions:
1. APPROVE - Code is production-ready with minor improvements
2. NEEDS_WORK - Significant issues that need addressing
3. NEEDS_REVIEW - Borderline case requiring human review
4. REJECT - Too many critical issues, major refactoring needed

Respond with:
Decision: [APPROVE/NEEDS_WORK/NEEDS_REVIEW/REJECT]
Reasoning: [Your detailed reasoning]
Confidence: [0.0-1.0]
"""
    
    def _create_modernization_prompt(
        self,
        project_data: Dict[str, Any],
        agent_results: List[Dict[str, Any]]
    ) -> str:
        """Create a prompt for modernization planning"""
        return f"""
Create a modernization roadmap for this project:

Project: {project_data.get('name', 'Unknown')}
Language: {project_data.get('language', 'Unknown')}
Framework: {project_data.get('framework', 'Unknown')}

Analysis Results:
{json.dumps(agent_results, indent=2)}

Create a phased modernization plan with:

1. Priority Actions (Week 1):
   - List 3-5 immediate critical fixes

2. Short-term Goals (Month 1-3):
   - List 5-7 important improvements

3. Long-term Vision (6-12 months):
   - List 3-5 strategic modernization goals

Format as JSON with keys: priority_actions, short_term_goals, long_term_vision
Each should be an array of strings.
"""
    
    def _parse_decision(
        self,
        decision_text: str,
        avg_score: float,
        critical_issues: int
    ) -> Dict[str, Any]:
        """Parse AI decision from text"""
        decision_text_upper = decision_text.upper()
        
        # Determine decision
        if "APPROVE" in decision_text_upper:
            decision = "APPROVE"
        elif "REJECT" in decision_text_upper:
            decision = "REJECT"
        elif "NEEDS_WORK" in decision_text_upper or "NEEDS WORK" in decision_text_upper:
            decision = "NEEDS_WORK"
        else:
            decision = "NEEDS_REVIEW"
        
        # Extract confidence
        confidence = 0.8
        if "confidence" in decision_text.lower():
            try:
                conf_str = decision_text.lower().split("confidence:")[1].split()[0]
                confidence = float(conf_str.strip())
            except:
                pass
        
        return {
            "decision": decision,
            "reasoning": decision_text,
            "confidence": confidence
        }
    
    def _parse_modernization_plan(self, plan_text: str) -> Dict[str, Any]:
        """Parse modernization plan from text"""
        try:
            # Try to extract JSON
            if "{" in plan_text and "}" in plan_text:
                json_start = plan_text.index("{")
                json_end = plan_text.rindex("}") + 1
                json_str = plan_text[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback to manual parsing
        return {
            "priority_actions": ["Review and fix security vulnerabilities"],
            "short_term_goals": ["Update dependencies", "Add test coverage"],
            "long_term_vision": ["Modernize architecture", "Improve scalability"]
        }
