import re
from core.models import Customer,Ticket

EMAIL=re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE=re.compile(r"(?<!\d)(?:\+?\d[\d\s-]{8,}\d)(?!\d)")
ORDER=re.compile(r"\b(?:order|ord|#)\s*[-:#]?\s*([A-Z0-9-]{4,})\b",re.I)

def extract_fields(text,ticket_id,ai_data=None):
    d=ai_data or {}
    email=d.get("email") or next(iter(EMAIL.findall(text)),None)
    phone=d.get("phone")
    if not phone:
        m=PHONE.search(text); phone=m.group(0).strip() if m else None
    order=d.get("order_id")
    if not order:
        m=ORDER.search(text); order=m.group(1) if m else None
    return Ticket(
        ticket_id=ticket_id,
        customer=Customer(d.get("customer_name"),email,phone),
        order_id=order,product=d.get("product"),
        issue=d.get("issue") or text.strip(),
        evidence=d.get("evidence") or [],
        sentiment=str(d.get("sentiment","neutral")).lower(),
        sentiment_score=float(d.get("sentiment_score",0) or 0),
        severity=str(d.get("severity","medium")).lower(),
        customer_impact=str(d.get("customer_impact","individual")).lower(),
        required_skill=str(d.get("required_skill","general")).lower())

def missing_mandatory_fields(t):
    missing=[]
    if not t.customer.name: missing.append("customer_name")
    if not (t.customer.email or t.customer.phone): missing.append("contact")
    if not t.issue.strip(): missing.append("issue")
    if not t.order_id and not re.search(r"\b(no|without|never)\s+order\b",t.issue,re.I):
        missing.append("order_id_or_no_order_confirmation")
    if not t.product and not re.search(r"\b(no|without|not related to)\s+(product|item)\b",t.issue,re.I):
        missing.append("product_or_no_product_confirmation")
    return missing

def build_missing_information_request(t):
    t.missing_fields=missing_mandatory_fields(t)
    q={
      "customer_name":"What is your full name?",
      "contact":"What email address or phone number should support use to contact you?",
      "issue":"Please describe the issue and the outcome you need.",
      "order_id_or_no_order_confirmation":"Please provide the order ID, or confirm this is not order-related.",
      "product_or_no_product_confirmation":"Which product/service is affected, or confirm that no specific product is involved.",
      "evidence":"Please provide relevant evidence such as a screenshot, receipt, transaction reference, or photo.",
      "evidence":"Please provide relevant evidence such as a screenshot, receipt, transaction reference, or photo."
    }
    return "\n".join("- "+q[x] for x in t.missing_fields)
