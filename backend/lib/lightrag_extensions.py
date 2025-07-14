import os
from dotenv import load_dotenv
from pathlib import Path
import logging
import logging.config

from backend.lib.cloudflareWorker import CloudflareWorker
from backend.lib.lightrag import QueryParam, LightRAG
from backend.lib.lightrag.kg.shared_storage import initialize_pipeline_status
from backend.lib.lightrag.utils import logger, set_verbose_debug, EmbeddingFunc

# Configuration
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env')
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY", "INSERT API KEY")
API_BASE_URL = os.getenv("CLOUDFLARE_API_BASE_URL", "INSERT YOUR API BASE URL")
LLM_MODEL = os.getenv("LLM_MODEL", "INSERT YOUR LLM MODEL HERE")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "INSERT YOUR EMBEDDING MODEL")
WORKING_DIR = f'.{os.getenv("WORKING_DIR", "INSERT YOUR WORKING DIR")}' # working directory located one level above this file's directory, supposedly.
USER_DATA_DIR = os.getenv("USER_DATA_IDR", "INSERT YOUR USER DATA DIR HERE")
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-this")

class MyLightRAG:
    def __init__(self):
        configure_logging()

        self.cloudflare_worker = CloudflareWorker(
            cloudflare_api_key=CLOUDFLARE_API_KEY,
            api_base_url=API_BASE_URL,
            embedding_model_name=EMBEDDING_MODEL,
            llm_model_name=LLM_MODEL,
        )

        self.rag = LightRAG(
            working_dir=WORKING_DIR,
            max_parallel_insert=2,
            llm_model_func=self.cloudflare_worker.query,
            llm_model_name=LLM_MODEL,
            llm_model_max_token_size=4080,
            embedding_func=EmbeddingFunc(
                embedding_dim=int(os.getenv("EMBEDDING_DIM", "1024")),
                max_token_size=int(os.getenv("MAX_EMBED_TOKENS", "2048")),
                func=lambda texts: self.cloudflare_worker.embedding_chunk(texts),
            ),
        )

    @classmethod
    async def create(cls):
        """Async factory method to safely initialize."""
        instance = cls()
        await instance.rag.initialize_storages()
        await initialize_pipeline_status()
        return instance

    async def createKG(self, book):
        if not os.path.exists(WORKING_DIR):
            os.mkdir(WORKING_DIR)

        try:
            test_text = ["This is a test string for embedding."]
            embedding = await self.rag.embedding_func(test_text)
            print(f"Embedding dimension: {embedding.shape[1]}")

            await self.rag.ainsert(book)

        except Exception as e:
            print(f"Error in createKG: {e}")

    async def query(self, query, mode):
        ALLOWED_MODES = {'hybrid', 'local', 'naive', 'global'}

        if mode.lower() in ALLOWED_MODES:
            resp = await self.rag.aquery(
                query=query,
                param=QueryParam(mode=mode.lower(), stream=True)
            )
            return resp

        return 'Invalid query mode'

def configure_logging():
    """Configure logging for the application"""

    # Reset any existing handlers to ensure clean configuration
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "lightrag"]:
        logger_instance = logging.getLogger(logger_name)
        logger_instance.handlers = []
        logger_instance.filters = []

    # Get log directory path from environment variable or use current directory
    log_dir = os.getenv("LOG_DIR", os.getcwd())
    log_file_path = os.path.abspath(os.path.join(log_dir, "lightrag_cloudflare_worker_demo.log"))

    print(f"\nLightRAG compatible demo log file: {log_file_path}\n")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # Get log file max size and backup count from environment variables
    log_max_bytes = int(os.getenv("LOG_MAX_BYTES", 10485760))  # Default 10MB
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))  # Default 5 backups

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(levelname)s: %(message)s",
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "file": {
                    "formatter": "detailed",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": log_file_path,
                    "maxBytes": log_max_bytes,
                    "backupCount": log_backup_count,
                    "encoding": "utf-8",
                },
            },
            "loggers": {
                "lightrag": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )

    # Set the logger level to INFO
    logger.setLevel(logging.INFO)
    # Enable verbose debug if needed
    set_verbose_debug(os.getenv("VERBOSE_DEBUG", "false").lower() == "true")

