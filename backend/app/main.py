from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.api.endpoints import invoices
import app.models.invoice  # noqa

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BizPulse API")
app.include_router(invoices.router)

@app.get("/health")
def health():
    return {"status": "ok"}