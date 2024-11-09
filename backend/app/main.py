from fastapi import FastAPI, HTTPException
from typing import Optional, Dict, Any
import logging
from firecrawl import FirecrawlApp
from .schemas import CrawlResponse, CrawlRequest
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add after app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firecrawl
firecrawl = FirecrawlApp(api_key="fc-d2296666afae4e06bf488bbf88a7733b")  # Replace with your API key

@app.post("/api/crawl", response_model=CrawlResponse)
async def crawl_endpoint(request: CrawlRequest):
    """
    API endpoint to initiate crawling of a website using Firecrawl.
    """
    try:
        url_str = str(request.url)
        crawl_status = firecrawl.crawl_url(
            url_str,
            params={
                'limit': 100,
                'scrapeOptions': {'formats': ['markdown', 'html']},
            },
            poll_interval=5
        )
        print(crawl_status)
        print(crawl_status.keys())        
        print(crawl_status['data'][0].keys())
        print(crawl_status['data'][1].keys())
        return CrawlResponse(data=crawl_status)

    except Exception as e:
        logging.error(f"Error during crawl: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crawl/{crawl_id}")
async def check_crawl_status(crawl_id: str):
    """
    Check the status of a crawl job.
    """
    try:
        status = firecrawl.check_crawl_status(crawl_id)
        return status
    except Exception as e:
        logging.error(f"Error checking crawl status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add this at the bottom of the file
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)