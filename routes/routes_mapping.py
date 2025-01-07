from fastapi import FastAPI
from routes.upload_routes import router as upload_router
from routes.chat_routes import router as chat_router
from routes.session_routes import router as session_router
from routes.history_routes import router as history_router
from routes.user import router as user_router

def include_routes(app: FastAPI):
    """
    Maps and includes all routes into the FastAPI app.
    """
    app.include_router(upload_router, prefix="/uploads", tags=["Uploads"])
    app.include_router(chat_router, prefix="/chat", tags=["Chat"])
    app.include_router(session_router, prefix="/sessions", tags=["Sessions"])
    app.include_router(history_router, prefix="/history", tags=["History"])
    app.include_router(user_router, prefix="/user", tags=["User"])


