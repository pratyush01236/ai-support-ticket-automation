import re

def mask_email(v):
    if not v:return v
    n,d=v.split("@",1);return n[:1]+"***@"+d
def mask_phone(v):
    if not v:return v
    d=re.sub(r"\D","",v);return "***"+d[-4:] if len(d)>=4 else "***"
def mask_order(v):
    if not v:return v
    return v[:2]+"***"+v[-2:] if len(v)>4 else "***"

def masked_summary(t):
    return f"""Ticket: {t.ticket_id}
Customer: {t.customer.name or "Unknown"}
Email: {mask_email(t.customer.email) or "Not provided"}
Phone: {mask_phone(t.customer.phone) or "Not provided"}
Order: {mask_order(t.order_id) or "Not provided"}
Product: {t.product or "Not provided"}
Issue: {t.issue}
Evidence: {", ".join(t.evidence) if t.evidence else "None"}
Sentiment: {t.sentiment} ({t.sentiment_score:.2f})
Severity: {t.severity}
Impact: {t.customer_impact}
Priority: {t.priority}
SLA: {t.sla_elapsed_minutes}/{t.sla_minutes} working minutes ({t.sla_warning=}, {t.sla_breached=})
Duplicate of: {t.duplicate_of or "None"}
Related: {", ".join(t.related_ticket_ids) or "None"}
Unrelated: {", ".join(t.unrelated_ticket_ids) or "None"}
Route: {t.routed_team or "Unassigned"} / {t.routed_agent or "Unassigned"}
Status: {t.status}
"""
