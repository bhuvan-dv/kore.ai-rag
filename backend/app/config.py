import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "kore-search-agent"
ENV = os.getenv("ENV", "development")
DOCUMENTS_DIR = "./data/documents"
