from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Annotated
import uvicorn

from main import SearchManager

app = FastAPI(
    title="API",
    description="API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_manager = SearchManager()

API_KEY = os.getenv("API_KEY")


def verify_api_key(key: Annotated[str | None, Header()] = None):
    if key is None:
        raise HTTPException(
            status_code=401,
            detail="API key missing",
            headers={"WWW-Authenticate": "APIKey"}
        )
    if key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "APIKey"}
        )
    return key


class SearchRequest(BaseModel):
    query: str
    enable_blog: Optional[bool] = True
    enable_news: Optional[bool] = True
    enable_google: Optional[bool] = True
    results_per_source: Optional[int] = 10


class SearchResult(BaseModel):
    title: str
    content: str
    url: str
    source: str


class SearchSummary(BaseModel):
    total_results: int
    sources_used: List[str]


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    summary: SearchSummary


@app.get("/")
async def root():
    return {
        "message": "Search API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/search (POST)",
            "docs": "/docs",
            "health": "/health"
        },
        "auth_info": {
            "required_header": "key",
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/search", response_model=SearchResponse)
async def search_integrated(request: SearchRequest, api_key: str = Depends(verify_api_key)):
    try:
        if not request.query or request.query.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty."
            )

        if request.results_per_source < 1 or request.results_per_source > 50:
            raise HTTPException(
                status_code=400,
                detail="results_per_source must be between 1 and 50."
            )

        if not any([request.enable_blog, request.enable_news, request.enable_google]):
            raise HTTPException(
                status_code=400,
                detail="At least one search source must be enabled."
            )

        search_results = search_manager.integrated_search(
            query=request.query.strip(),
            enable_blog=request.enable_blog,
            enable_news=request.enable_news,
            enable_google=request.enable_google,
            results_per_source=request.results_per_source
        )

        return SearchResponse(
            query=search_results["query"],
            results=[
                SearchResult(
                    title=item["title"],
                    content=item["content"],
                    url=item["url"],
                    source=item["source"]
                ) for item in search_results["results"]
            ],
            summary=SearchSummary(
                total_results=search_results["summary"]["total_results"],
                sources_used=search_results["summary"]["sources_used"]
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/search/{query}")
async def search_simple(
    query: str,
    enable_blog: bool = True,
    enable_news: bool = True,
    enable_google: bool = True,
    results_per_source: int = 5,
    api_key: str = Depends(verify_api_key)
):
    try:
        request = SearchRequest(
            query=query,
            enable_blog=enable_blog,
            enable_news=enable_news,
            enable_google=enable_google,
            results_per_source=results_per_source
        )
        return await search_integrated(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}"
        )


@app.get("/api-status")
async def api_status(api_key: str = Depends(verify_api_key)):
    return {
        "naver_api": {
            "client_id_configured": bool(search_manager.naver_client_id),
            "client_secret_configured": bool(search_manager.naver_client_secret)
        },
        "google_api": {
            "api_key_configured": bool(search_manager.google_api_key),
            "cse_id_configured": bool(search_manager.google_cse_id)
        },
        "authentication": {
            "status": "authenticated"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
