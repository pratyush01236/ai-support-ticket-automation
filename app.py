import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from config import *
from ai.extractor import extract_with_gemini
from core.extraction import extract_fields,build_missing_information_request
from core.priority import calculate_priority
from core.sla import BusinessCalendar,SLAEngine
from core.routing import Agent,RoutingEngine
from core.duplicates import find_duplicate,group_related,separate_unrelated
from core.handoff import masked_summary

TICKETS=[]

def process(conversation,now=None):
    now=now or datetime.now(ZoneInfo(TIMEZONE))
    data=extract_with_gemini(conversation)
    t=extract_fields(conversation,"TKT-"+uuid.uuid4().hex[:8].upper(),data)
    t.created_at=now
    missing=build_missing_information_request(t)
    cal=BusinessCalendar(TIMEZONE,BUSINESS_START,BUSINESS_END,WEEKENDS,HOLIDAYS)
    sla=SLAEngine(cal,get_sla_rules())
    calculate_priority(t)
    sla.apply(t,now)
    calculate_priority(t,t.sla_minutes-t.sla_elapsed_minutes)
    sla_result=sla.apply(t,now)
    find_duplicate(t,TICKETS); group_related(t,TICKETS); separate_unrelated(t,TICKETS)
    agents=[
      Agent("Aarav",{"payments","billing","general"},True,3,10,"Billing"),
      Agent("Meera",{"shipping","orders","general"},True,5,10,"Orders"),
      Agent("Kabir",{"technical","general"},True,2,10,"Technical"),
      Agent("OnCall",{"general","payments","orders","technical"},True,1,10,"OnCall",True)]
    route=RoutingEngine(agents,int(BUSINESS_START[:2]),int(BUSINESS_END[:2])).route(t,now)
    TICKETS.append(t)
    return t,missing,sla_result,route

def main():
    text=input("Paste unresolved conversation:\n> ")
    t,missing,sla,route=process(text)
    if missing:print("\nMISSING INFORMATION:\n"+missing)
    print("\n=== MASKED HANDOFF ===\n"+masked_summary(t))
    print("SLA:",sla);print("ROUTING:",route)

if __name__=="__main__":main()
