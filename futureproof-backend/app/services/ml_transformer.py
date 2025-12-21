"""
ML/DL Specialized Transformer
Transforms TensorFlow → PyTorch, modernizes scikit-learn, optimizes ML code
"""

import logging
import json
from typing import Dict, Any, List
from app.services.groq_service import GroqService

logger = logging.getLogger(__name__)


class MLTransformerService:
    """
    Specialized transformer for Machine Learning and Deep Learning code
    """
    
    def __init__(self):
        self.groq_service = GroqService()
        
        # 2028 ML/DL Standards
        self.ml_standards_2028 = {
            "deep_learning": {
                "framework": "PyTorch 2.5+ or TensorFlow 2.18+",
                "features": [
                    "PyTorch 2.5 torch.compile() for 2x speed",
                    "Automatic Mixed Precision (AMP)",
                    "Distributed training with DDP/FSDP",
                    "Model quantization and pruning",
                    "ONNX export for deployment",
                    "Weights & Biases / MLflow integration",
                    "Type hints everywhere",
                    "Pytest for model testing",
                    "Docker + GPU support",
                    "Hugging Face integration"
                ]
            },
            "machine_learning": {
                "framework": "scikit-learn 1.5+, XGBoost 2.1+",
                "features": [
                    "Pipeline-based workflows",
                    "Feature engineering automation",
                    "Hyperparameter optimization (Optuna)",
                    "Model versioning (MLflow)",
                    "A/B testing framework",
                    "Explainability (SHAP)",
                    "Production monitoring",
                    "FastAPI inference API"
                ]
            }
        }
    
    async def transform_ml_code(
        self,
        file_path: str,
        original_code: str,
        ml_frameworks: List[str],
        project_type: str
    ) -> Dict[str, Any]:
        """Transform ML/DL code to 2028 standards"""
        
        logger.info(f"Transforming ML code: {file_path}, frameworks: {ml_frameworks}")
        
        # Determine transformation strategy
        if 'tensorflow' in ml_frameworks or 'keras' in ml_frameworks:
            return await self._transform_tensorflow_to_pytorch(original_code, file_path)
        elif 'pytorch' in ml_frameworks:
            return await self._modernize_pytorch(original_code, file_path)
        elif 'scikit-learn' in ml_frameworks:
            return await self._modernize_sklearn(original_code, file_path)
        else:
            return await self._generic_ml_transform(original_code, file_path)
    
    async def _transform_tensorflow_to_pytorch(
        self,
        original_code: str,
        file_path: str
    ) -> Dict[str, Any]:
        """Convert TensorFlow/Keras to modern PyTorch"""
        
        prompt = f"""You are an expert ML engineer. Convert this TensorFlow/Keras code to modern PyTorch 2.5+.

ORIGINAL CODE ({file_path}):

APPLY THESE TRANSFORMATIONS:

1. **Framework Migration**:
   - Convert TensorFlow layers → PyTorch nn.Module
   - Convert Keras Sequential → PyTorch Sequential or custom Module
   - Update data loading to PyTorch DataLoader
   - Convert optimizers (Adam, SGD, etc.)

2. **Modern PyTorch 2.5 Features**:
   - Use torch.compile() for 2x speed
   - Add Automatic Mixed Precision (AMP)
   - Implement proper training loop with tqdm
   - Add model checkpointing
   - Use torch.nn.functional where appropriate

3. **Best Practices**:
   - Full type hints
   - Proper device handling (cuda/mps/cpu)
   - Reproducibility (seeds, deterministic)
   - Logging with print or logger
   - Model summary

4. **Production Ready**:
   - ONNX export functionality
   - Model quantization support
   - Batch inference optimization

OUTPUT (JSON):
{{
  "code": "transformed PyTorch code here",
  "improvements": ["list of improvements"],
  "migration_notes": ["important changes"],
  "performance_gain": "estimated improvement",
  "dependencies": ["torch>=2.5.0", "torchvision>=0.20.0"]
}}

Generate ONLY valid JSON."""

        return await self._call_ai_transform(prompt)
    
    async def _modernize_pytorch(self, original_code: str, file_path: str) -> Dict[str, Any]:
        """Modernize existing PyTorch code to 2.5+ standards"""
        
        prompt = f"""Modernize this PyTorch code to PyTorch 2.5+ with latest best practices.

CODE ({file_path}):

ADD:
1. torch.compile() for 2x performance
2. Automatic Mixed Precision
3. Distributed training support (DDP)
4. Modern optimizers (AdamW with weight decay)
5. Learning rate schedulers (OneCycleLR)
6. Model checkpointing with best weights
7. Type hints and docstrings
8. ONNX export
9. Production inference optimization

OUTPUT (JSON with "code", "improvements", "dependencies", "performance_gain")"""

        return await self._call_ai_transform(prompt)
    
    async def _modernize_sklearn(self, original_code: str, file_path: str) -> Dict[str, Any]:
        """Modernize scikit-learn code"""
        
        prompt = f"""Modernize this scikit-learn code to 2028 standards.

CODE:

ADD:
1. Pipeline-based workflow
2. ColumnTransformer for feature engineering
3. GridSearchCV → Optuna for hyperparameter tuning
4. Model persistence with joblib
5. MLflow for experiment tracking
6. Cross-validation strategies
7. Feature importance analysis
8. Type hints and comprehensive docstrings

OUTPUT (JSON with "code", "improvements", "dependencies")"""

        return await self._call_ai_transform(prompt)
    
    async def _generic_ml_transform(self, original_code: str, file_path: str) -> Dict[str, Any]:
        """Generic ML code modernization"""
        return {
            "code": original_code,
            "improvements": ["Generic ML transform - manual review needed"],
            "dependencies": [],
            "performance_gain": "Unknown"
        }
    
    async def _call_ai_transform(self, prompt: str) -> Dict[str, Any]:
        """Helper to call AI transformation"""
        try:
            response = await self.groq_service.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert ML engineer. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000,
                timeout=30
            )
            
            result_text = response.choices[0].message.content
            
            # Extract JSON
            if "```" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("``````")[0].strip()
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            logger.error(f"AI transformation failed: {str(e)}")
            return {
                "code": "",
                "improvements": [],
                "error": str(e),
                "dependencies": []
            }
