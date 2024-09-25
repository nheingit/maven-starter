from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
from .database import get_db, initialize_database
from .schemas import Application, Module, Function, Parameter, Example, ScrapeRequest
from .scraper import scrape_hexdoc

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

initialize_database()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Update this with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def background_scrape(url: str):
    try:
        result = scrape_hexdoc(url)
        logger.info(f"Crawling completed: {result}")
    except Exception as e:
        logger.error(f"Error during crawling: {str(e)}")

@app.post("/api/scrape")
def start_scraping(scrape_request: ScrapeRequest, background_tasks: BackgroundTasks):
    logger.info(f"Starting scraping for URL: {scrape_request.url}")
    background_tasks.add_task(background_scrape, scrape_request.url)
    return {"message": "Scraping started in the background."}

@app.get("/api/applications", response_model=List[Application])
def get_applications():
    logger.info("Fetching all applications")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, version, description FROM applications")
        apps = cursor.fetchall()
    return [Application(id=app[0], name=app[1], version=app[2], description=app[3]) for app in apps]

@app.get("/api/applications/{app_id}/modules", response_model=List[Module])
def get_modules(app_id: int):
    logger.info(f"Fetching modules for application ID: {app_id}")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM modules WHERE application_id = ?", (app_id,))
        modules = cursor.fetchall()
    return [Module(id=mod[0], name=mod[1], description=mod[2]) for mod in modules]

@app.get("/api/modules/{module_id}/functions", response_model=List[Function])
def get_functions(module_id: int):
    logger.info(f"Fetching functions for module ID: {module_id}")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, arity, return_type, summary, description 
            FROM functions WHERE module_id = ?
        """, (module_id,))
        functions = cursor.fetchall()
        function_list = []
        for func in functions:
            function_id = func[0]
            # Get parameters
            cursor.execute("""
                SELECT id, name, type, default_value, description
                FROM parameters WHERE function_id = ?
            """, (function_id,))
            params = cursor.fetchall()
            parameters = [Parameter(id=p[0], name=p[1], type=p[2], default_value=p[3], description=p[4]) for p in params]

            # Get examples
            cursor.execute("""
                SELECT id, code, description
                FROM examples WHERE function_id = ?
            """, (function_id,))
            exs = cursor.fetchall()
            examples = [Example(id=e[0], code=e[1], description=e[2]) for e in exs]

            function_item = Function(
                id=func[0],
                name=func[1],
                arity=func[2],
                return_type=func[3],
                summary=func[4],
                description=func[5],
                parameters=parameters,
                examples=examples
            )
            function_list.append(function_item)
    return function_list
