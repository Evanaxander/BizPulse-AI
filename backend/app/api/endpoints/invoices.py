import json
import base64
from io import BytesIO
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from groq import Groq
from PIL import Image

from app.db.session import get_db
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceOut, WeeklySummary
from app.core.config import get_settings

router = APIRouter(prefix="/invoices", tags=["invoices"])
settings = get_settings()


def extract_invoice_with_groq(image_bytes: bytes, content_type: str) -> dict:
    """Send image to Groq Vision and extract invoice data."""
    client = Groq(api_key=settings.groq_api_key)

    # Convert to base64
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """You are an invoice data extraction assistant. 
    Extract the following from this invoice image and return ONLY valid JSON:
    {
        "vendor": "company/shop name",
        "amount": 0.00,
        "currency": "BDT",
        "invoice_date": "YYYY-MM-DD or as shown",
        "items": ["item1 - price", "item2 - price"],
        "confidence": "high/medium/low"
    }
    If a field is not visible, use null. Return only JSON, no explanation."""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{content_type};base64,{b64_image}"
                    }
                },
                {"type": "text", "text": prompt}
            ]
        }],
        max_tokens=500
    )

    raw = response.choices[0].message.content.strip()
    # Clean JSON if wrapped in markdown
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


@router.post("/process-image", response_model=InvoiceOut)
async def process_invoice_image(
    file: UploadFile = File(...),
    uploaded_by: str = Form(default="whatsapp_user"),
    db: Session = Depends(get_db)
):
    """Receive an invoice image, extract data with Groq Vision, store in DB."""
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Only JPEG, PNG, or WebP images allowed")

    image_bytes = await file.read()

    try:
        extracted = extract_invoice_with_groq(image_bytes, file.content_type)
    except Exception as e:
        raise HTTPException(500, f"OCR extraction failed: {str(e)}")

    invoice = Invoice(
        vendor=extracted.get("vendor") or "Unknown",
        amount=float(extracted.get("amount") or 0.0),
        currency=extracted.get("currency") or "BDT",
        invoice_date=extracted.get("invoice_date"),
        items=json.dumps(extracted.get("items") or []),
        raw_text=str(extracted),
        uploaded_by=uploaded_by
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/weekly-summary", response_model=WeeklySummary)
def get_weekly_summary(db: Session = Depends(get_db)):
    """Return this week's expense summary."""
    week_ago = datetime.utcnow() - timedelta(days=7)

    invoices = db.scalars(
        select(Invoice).where(Invoice.created_at >= week_ago)
        .order_by(Invoice.created_at.desc())
    ).all()

    total = sum(i.amount for i in invoices)
    vendors = list({i.vendor for i in invoices})

    return WeeklySummary(
        total_expenses=round(total, 2),
        currency="BDT",
        invoice_count=len(invoices),
        top_vendors=vendors[:5],
        invoices=invoices
    )


@router.get("/", response_model=list[InvoiceOut])
def list_invoices(db: Session = Depends(get_db)):
    return db.scalars(select(Invoice).order_by(Invoice.created_at.desc())).all()