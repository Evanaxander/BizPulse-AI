from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vendor: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="BDT")
    invoice_date: Mapped[str] = mapped_column(String(50), nullable=True)
    items: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    raw_text: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    uploaded_by: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)