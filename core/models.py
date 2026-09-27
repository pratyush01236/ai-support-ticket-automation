from dataclasses import dataclass,field
from datetime import datetime

@dataclass
class Customer:
    name:str|None=None
    email:str|None=None
    phone:str|None=None

@dataclass
class Ticket:
    ticket_id:str
    customer:Customer=field(default_factory=Customer)
    order_id:str|None=None
    product:str|None=None
    issue:str=""
    evidence:list[str]=field(default_factory=list)
    sentiment:str="neutral"
    sentiment_score:float=0.0
    severity:str="medium"
    customer_impact:str="individual"
    waiting_minutes:int=0
    created_at:datetime=field(default_factory=datetime.now)
    unresolved:bool=True
    status:str="open"
    priority:str="medium"
    sla_minutes:int=480
    sla_elapsed_minutes:int=0
    sla_warning:bool=False
    sla_breached:bool=False
    required_skill:str="general"
    missing_fields:list[str]=field(default_factory=list)
    duplicate_of:str|None=None
    related_ticket_ids:list[str]=field(default_factory=list)
    unrelated_ticket_ids:list[str]=field(default_factory=list)
    routed_team:str|None=None
    routed_agent:str|None=None
    routing_reason:str|None=None\n    escalated:bool=False\n    escalation_reason:str|None=None
