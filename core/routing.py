from dataclasses import dataclass
from datetime import datetime

@dataclass
class Agent:
    name:str
    skills:set[str]
    available:bool=True
    workload:int=0
    max_workload:int=10
    team:str="general"
    on_call:bool=False
    @property
    def capacity(self): return max(0,self.max_workload-self.workload)

class RoutingEngine:
    def __init__(self,agents,business_start=9,business_end=18):
        self.agents=agents; self.business_start=business_start; self.business_end=business_end
    def route(self,ticket,now):
        business=now.weekday()<5 and self.business_start<=now.hour<self.business_end
        candidates=[a for a in self.agents if a.available and a.capacity>0 and (ticket.required_skill in a.skills or "general" in a.skills)]
        if not business:
            candidates=[a for a in candidates if a.on_call]
            if not candidates:
                ticket.status="queued_after_hours"; ticket.routing_reason="No eligible on-call agent"; return self._result(ticket)
        if not candidates:
            ticket.status="queued"; ticket.routing_reason="No available agent with required skill/capacity"; return self._result(ticket)
        a=sorted(candidates,key=lambda x:(-x.capacity,x.workload,x.name))[0]
        a.workload+=1; ticket.routed_team=a.team; ticket.routed_agent=a.name
        ticket.status="assigned"; ticket.routing_reason=f"Matched skill={ticket.required_skill}"
        return self._result(ticket)
    def _result(self,t):
        return {"status":t.status,"team":t.routed_team,"agent":t.routed_agent,"reason":t.routing_reason}
