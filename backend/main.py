from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="SEO Scraper API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

class SEOScore(BaseModel):
    url: str
    score: int
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_count: int = 0
    image_alt_missing: int = 0

@app.get("/")
async def root():
    return {"message": "SEO Scraper API"}

@app.post("/analyze", response_model=SEOScore)
async def analyze_seo(request: URLRequest):
    # Placeholder for SEO analysis logic
    return SEOScore(
        url=request.url,
        score=85,
        title="Sample Title",
        meta_description="Sample meta description",
        h1_count=1,
        image_alt_missing=0
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}