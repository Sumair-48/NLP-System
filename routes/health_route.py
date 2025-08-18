from fastapi import APIRouter,status

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/",
            status_code=status.HTTP_200_OK)

async def read_root():
    return {"message": "Task Management Chat Service is running!",
             "status": "healthy"
             }


@router.get("/health",
             status_code=status.HTTP_200_OK)

async def health_check():
    return {
        "status": "healthy",
        "service": "task-management-chat",
        "version": "1.0.0"
    }
