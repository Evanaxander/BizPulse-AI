from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InvoiceCreate(BaseModel):
    vendor: str
    amount: float
    currency: str = "BDT"
    invoice_date: Optional[str] = None
    items: Optional[str] = None
    raw_text: Optional[str] = None
    uploaded_by: Optional[str] = None

class InvoiceOut(InvoiceCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class WeeklySummary(BaseModel):
    total_expenses: float
    currency: str
    invoice_count: int
    top_vendors: list[str]
    invoices: list[InvoiceOut]