from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from api.controllers import journal_router
import logging
import uvicorn

load_dotenv()

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(journal_router)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    logger.info("Journal API started")
    uvicorn.run(app, host="127.0.0.1", port=8000)
    logger.info ("Journal API stopped")
