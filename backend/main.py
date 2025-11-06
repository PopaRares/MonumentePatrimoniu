from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from models import Base, Monument, MonumentResponse, PaginatedMonumentsResponse
from env import DATABASE_URL

app = FastAPI(title="Patrimoniu API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
database_url = DATABASE_URL
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
async def health():
    try:
        # Test database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/monuments", response_model=PaginatedMonumentsResponse)
async def get_monuments(
    county: str = Query(..., description="County name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get monuments by county with pagination."""
    skip = (page - 1) * page_size
    
    # Query monuments filtered by county, ordered by id (Nr. crt.)
    query = db.query(Monument).filter(Monument.county == county).order_by(Monument.id)
    total = query.count()
    monuments = query.offset(skip).limit(page_size).all()
    
    return PaginatedMonumentsResponse(
        count=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
        results=[MonumentResponse.model_validate(m) for m in monuments]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

