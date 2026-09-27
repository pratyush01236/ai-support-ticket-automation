from datetime import datetime
from zoneinfo import ZoneInfo
from core.models import Ticket,Customer
from core.sla import BusinessCalendar,SLAEngine
from core.routing import Agent,RoutingEngine
from core.duplicates import find_duplicate,group_related
from core.priority import calculate_priority
TZ=ZoneInfo("Asia/Kolkata")

def ticket(i,issue,order="ORD-123",skill="general"):
    return Ticket(i,Customer("Test","test@example.com"),order,"Laptop",issue,required_skill=skill)

def test_duplicate():
    a=ticket("T1","I was charged twice for my laptop order")
    b=ticket("T2","My laptop order was charged twice")
    assert find_duplicate(b,[a])[0]=="T1"

def test_related():
    a=ticket("T1","Laptop order has not arrived","ORD-1")
    b=ticket("T2","Laptop shipment is delayed","ORD-2")
    assert "T1" in group_related(b,[a],.35)

def test_unavailable_team():
    t=ticket("T1","Payment failed",skill="payments")
    r=RoutingEngine([Agent("Billing",{"payments"},False,0,10)]).route(t,datetime(2026,9,28,11,tzinfo=TZ))
    assert r["status"]=="queued"

def test_after_hours():
    t=ticket("T1","System is down",skill="technical")
    a=[Agent("Tech",{"technical"},True,0,10,"Technical"),Agent("OnCall",{"technical"},True,2,10,"OnCall",True)]
    assert RoutingEngine(a).route(t,datetime(2026,9,28,21,tzinfo=TZ))["team"]=="OnCall"

def test_after_hours_no_oncall():
    t=ticket("T1","Technical issue",skill="technical")
    a=[Agent("Tech",{"technical"},True,0,10,"Technical")]
    assert RoutingEngine(a).route(t,datetime(2026,9,28,21,tzinfo=TZ))["status"]=="queued_after_hours"

def test_sla_weekend_holiday():
    c=BusinessCalendar(holidays={"2026-10-02"})
    e=SLAEngine(c,{"high":240})
    r=e.evaluate(datetime(2026,10,1,17,tzinfo=TZ),datetime(2026,10,5,10,tzinfo=TZ),"high")
    assert r["elapsed_minutes"]==120

def test_warning():
    c=BusinessCalendar();e=SLAEngine(c,{"high":240})
    r=e.evaluate(datetime(2026,9,28,9,tzinfo=TZ),datetime(2026,9,28,12,tzinfo=TZ),"high")
    assert r["warning"] and not r["breached"]

def test_breach():
    c=BusinessCalendar();e=SLAEngine(c,{"high":240})
    r=e.evaluate(datetime(2026,9,28,9,tzinfo=TZ),datetime(2026,9,28,13,tzinfo=TZ),"high")
    assert r["breached"]

def test_runtime_sla_change():
    c=BusinessCalendar();e=SLAEngine(c,{"high":240})
    s=datetime(2026,9,28,9,tzinfo=TZ);n=datetime(2026,9,28,11,tzinfo=TZ)
    assert not e.evaluate(s,n,"high")["breached"]
    e.rules["high"]=90
    assert e.evaluate(s,n,"high")["breached"]

def test_priority():
    t=ticket("T1","Refund pending");t.severity="high";t.sentiment="negative";t.customer_impact="multiple";t.waiting_minutes=300
    assert calculate_priority(t) in {"high","critical"}
