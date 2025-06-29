from fastapi import FastAPI
from dotenv import load_dotenv
from api.controllers import journal_router
import logging
import uvicorn

load_dotenv()

# TODO: Setup basic console logging
# Hint: Use logging.basicConfig() with level=logging.INFO




app = FastAPI()
app.include_router(journal_router)

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)
logging.info("Journal API started")
uvicorn.run(app, host="0.0.0.0", port=8000)
logging.info ("Journal API stopped")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)