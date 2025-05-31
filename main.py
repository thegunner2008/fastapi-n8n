import logging

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api_router import router
from app.core.config import settings
from app.helpers.exception_handler import CustomException, http_exception_handler

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE, disable_existing_loggers=False)


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME, docs_url="/docs", redoc_url='/re-docs',
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        description='''
        Support API for the N8N
        '''
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router, prefix=settings.API_PREFIX)
    application.add_exception_handler(CustomException, http_exception_handler)

    return application


app = get_application()
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
