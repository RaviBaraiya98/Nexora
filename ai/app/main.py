from fastapi import FastAPI
from .analyzer import analyze_answer
from .schemas import AnalyzeRequest, AnalysisResponse

app = FastAPI(title="Nexora AI Service", version="0.1.0")

@app.get('/health')
def health():
    return {'service': 'nexora-ai', 'status': 'ok'}

@app.post('/v1/analyze', response_model=AnalysisResponse)
async def analyze(request: AnalyzeRequest):
    return await analyze_answer(request)
