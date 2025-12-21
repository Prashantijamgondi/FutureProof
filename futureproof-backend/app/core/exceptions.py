class FutureProofException(Exception):
    """Base exception for FutureProof"""
    pass

class RepositoryCloneError(FutureProofException):
    """Raised when repository cloning fails"""
    pass

class AnalysisError(FutureProofException):
    """Raised when analysis fails"""
    pass

class AgentExecutionError(FutureProofException):
    """Raised when agent execution fails"""
    pass
