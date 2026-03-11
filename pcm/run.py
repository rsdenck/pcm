"""
PCM API Runner
Execute este arquivo para iniciar a API
"""
import uvicorn
from pcm.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "pcm.services.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_debug,
        log_level=settings.log_level.lower(),
    )
