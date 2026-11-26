from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    company: str = Field(min_length=2)
    role: str = Field(min_length=2)
    question: str = Field(min_length=2)
    answer: str = Field(min_length=1)


class AnalysisResponse(BaseModel):
    technical_relevance: int
    concept_coverage: int
    answer_structure: int
    communication: int
    detected: list[str]
    missing: list[str]
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    source: str
    # Experimental score; not a validated real-world interview score.
    predicted_answer_quality_score: float | None = None
