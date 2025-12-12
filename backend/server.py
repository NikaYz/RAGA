# # backend/server.py
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List
# import logging
# import logging.config
# import os
# import time
# import threading
# import pickle
# import faiss

# # 🟢 Import the corrected Pipeline class
# from pipeline.pipeline import Pipeline 

# # load logging config
# try:
#     logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
# except Exception:
#     logging.basicConfig(level=logging.INFO)

# logger = logging.getLogger("rag")

# # --- REMOVED: Redundant GEMINI_API_KEY loading logic ---

# # pipeline index management
# INDEX_FILE = "pipeline/cache/vector.index"
# META_FILE = "pipeline/cache/metadata.pkl"

# index = None
# id_to_meta = None
# _index_mtime = None
# _index_lock = threading.Lock()
# # 🟢 Global variable for the RAG pipeline instance
# pipeline_instance: Pipeline = None 

# def load_index():
#     global index, id_to_meta, _index_mtime
#     with _index_lock:
#         if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
#             try:
#                 mtime = os.path.getmtime(INDEX_FILE)
#                 if _index_mtime is None or mtime != _index_mtime:
#                     logger.info("Loading FAISS index from disk...")
#                     index = faiss.read_index(INDEX_FILE)
#                     with open(META_FILE, "rb") as f:
#                         id_to_meta = pickle.load(f)
#                     _index_mtime = mtime
#                     logger.info("FAISS index loaded. docs=%s", len(id_to_meta))
#             except Exception as e:
#                 logger.exception("Failed to load index: %s", e)
#         else:
#             logger.warning("Index or metadata missing. Run build_embeddings to create them.")

# # background thread to watch for index changes
# def index_watcher(interval=10):
#     while True:
#         try:
#             load_index()
#         except Exception as e:
#             logger.exception("Index watcher error: %s", e)
#         time.sleep(interval)

# # start watcher thread
# threading.Thread(target=index_watcher, daemon=True).start()

# # Pydantic models
# class QueryRequest(BaseModel):
#     query: str

# class QueryResponse(BaseModel):
#     answer: str
#     sources: List[str]



# app = FastAPI(title="Shakespeare Query", version="1.0.0")

# @app.on_event("startup")
# def startup():
#     global pipeline_instance
#     load_index()
#     try:
#         # 🟢 Initialize the Pipeline instance here
#         pipeline_instance = Pipeline() 
#         logger.info("RAG Pipeline initialized successfully.")
#     except Exception as e:
#         logger.error("Failed to initialize RAG Pipeline (check GEMINI_API_KEY): %s", e)
#         # If the key is bad, the Pipeline constructor will raise ValueError
        
#     logger.info("Server startup complete")

# @app.post("/query", response_model=QueryResponse)
# async def query_endpoint(request: QueryRequest):
#     global pipeline_instance
#     if pipeline_instance is None:
#         raise HTTPException(status_code=503, detail="RAG Pipeline not initialized. Check startup logs.")
        
#     try:
#         logger.info("Received query: %s", request.query)
        
#         # 🟢 Call the fully functional pipeline.__call__ method
#         answer, docs = pipeline_instance(request.query)
        
#         # Log user-visible event
#         logger.info("Answered query; sources=%d", len(docs))
        
#         # The 'docs' variable now holds the source metadata from the pipeline
#         return QueryResponse(answer=answer, sources=[str(d) for d in docs])
        
#     except Exception as e:
#         logger.exception("Error handling query: %s", e)
#         # Any API error from Gemini will now be caught and logged here
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging
import logging.config
import os
import time
import threading
import pickle
import faiss
import logstash

# 🟢 Import the corrected Pipeline class
from pipeline.pipeline import Pipeline  

# --- Logging Configuration ---
# LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", "logstash")  # Service name in k8s
# LOGSTASH_PORT = int(os.getenv("LOGSTASH_PORT", 5000))
LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", "logstash")
# Use a different environment variable name to avoid the K8s collision
LOGSTASH_PORT = int(os.getenv("LOGSTASH_TCP_PORT", 5000))

# Load logging configuration from file
try:
    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
except Exception:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("rag")

# Attach Logstash handler
try:
    logstash_handler = logstash.TCPLogstashHandler(LOGSTASH_HOST, LOGSTASH_PORT, version=1)
    logger.addHandler(logstash_handler)
    logger.info("Logstash handler attached successfully")
except Exception as e:
    logger.warning("Failed to attach Logstash handler: %s", e)

# --- FAISS Pipeline Index Management ---
INDEX_FILE = "pipeline/cache/vector.index"
META_FILE = "pipeline/cache/metadata.pkl"

index = None
id_to_meta = None
_index_mtime = None
_index_lock = threading.Lock()
pipeline_instance: Pipeline = None  # Global pipeline instance

def load_index():
    global index, id_to_meta, _index_mtime
    with _index_lock:
        if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
            try:
                mtime = os.path.getmtime(INDEX_FILE)
                if _index_mtime is None or mtime != _index_mtime:
                    logger.info("Loading FAISS index from disk...")
                    index = faiss.read_index(INDEX_FILE)
                    with open(META_FILE, "rb") as f:
                        id_to_meta = pickle.load(f)
                    _index_mtime = mtime
                    logger.info("FAISS index loaded. docs=%s", len(id_to_meta))
            except Exception as e:
                logger.exception("Failed to load index: %s", e)
        else:
            logger.warning("Index or metadata missing. Run build_embeddings to create them.")

# Background thread to watch for index changes
def index_watcher(interval=10):
    while True:
        try:
            load_index()
        except Exception as e:
            logger.exception("Index watcher error: %s", e)
        time.sleep(interval)

threading.Thread(target=index_watcher, daemon=True).start()

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

# --- FastAPI App ---
app = FastAPI(title="Shakespeare Query", version="1.0.0")

def attach_logstash_with_retry(host, port, logger, max_retries=5, delay=5):
    import time
    import socket
    
    for attempt in range(max_retries):
        try:
            # Test socket first
            with socket.create_connection((host, port), timeout=2):
                pass
            
            # If socket works, attach handler
            handler = logstash.TCPLogstashHandler(host, port, version=1)
            logger.addHandler(handler)
            logger.info(f"✅ Logstash connected on {host}:{port}")
            return
        except (OSError, ConnectionRefusedError) as e:
            logger.warning(f"⏳ Logstash not ready yet (Attempt {attempt+1}/{max_retries})...")
            time.sleep(delay)
    
    logger.error("❌ Could not connect to Logstash after retries. Logs will be local only.")

@app.on_event("startup")
def startup():
    global pipeline_instance
    # try:
    #     logger.info("🔌 Connecting to Logstash at %s:%s...", LOGSTASH_HOST, LOGSTASH_PORT)
    #     logstash_handler = logstash.TCPLogstashHandler(LOGSTASH_HOST, LOGSTASH_PORT, version=1)
    #     logger.addHandler(logstash_handler)
    #     logger.info("✅ Logstash handler attached successfully!")
    # except Exception as e:
    #     logger.warning("❌ Failed to attach Logstash: %s", e)
    # # -
    threading.Thread(
        target=attach_logstash_with_retry, 
        args=(LOGSTASH_HOST, LOGSTASH_PORT, logger)
    ).start()
    load_index()
    try:
        pipeline_instance = Pipeline()
        logger.info("RAG Pipeline initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize RAG Pipeline (check GEMINI_API_KEY): %s", e)
    logger.info("Server startup complete")

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    global pipeline_instance
    if pipeline_instance is None:
        raise HTTPException(status_code=503, detail="RAG Pipeline not initialized. Check startup logs.")
    try:
        logger.info("Received query: %s", request.query)
        answer, docs = pipeline_instance(request.query)
        logger.info("Answered query; sources=%d", len(docs))
        return QueryResponse(answer=answer, sources=[str(d) for d in docs])
    except Exception as e:
        logger.exception("Error handling query: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
