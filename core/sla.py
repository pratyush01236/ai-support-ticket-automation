from datetime import datetime,date,time,timedelta
from zoneinfo import ZoneInfo

class BusinessCalendar:
    def __init__(self,timezone="Asia/Kolkata",business_start="09:00",business_end="18:00",weekends=None,holidays=None):
        self.tz=ZoneInfo(timezone)
        self.business_start=time.fromisoformat(business_start)
        self.business_end=time.fromisoformat(business_end)
        self.weekends=set({5,6} if weekends is None else weekends)
        self.holidays=set(holidays or [])
    def is_business_day(self,d):
        return d.weekday() not in self.weekends and d.isoformat() not in self.holidays
    def window(self,d):
        return datetime.combine(d,self.business_start,self.tz),datetime.combine(d,self.business_end,self.tz)
    def working_minutes_between(self,start,end):
        if end<=start:return 0
        start,end=start.astimezone(self.tz),end.astimezone(self.tz)
        total=0; d=start.date()
        while d<=end.date():
            if self.is_business_day(d):
                ws,we=self.window(d); left=max(start,ws); right=min(end,we)
                if right>left: total+=(right-left).total_seconds()/60
            d+=timedelta(days=1)
        return int(total)
    def add_working_minutes(self,start,minutes):
        cur=start.astimezone(self.tz); left=max(0,int(minutes))
        while left:
            if not self.is_business_day(cur.date()):
                cur=datetime.combine(cur.date()+timedelta(days=1),self.business_start,self.tz); continue
            ws,we=self.window(cur.date())
            if cur<ws:cur=ws
            if cur>=we:
                cur=datetime.combine(cur.date()+timedelta(days=1),self.business_start,self.tz); continue
            available=int((we-cur).total_seconds()/60); step=min(left,available)
            cur+=timedelta(minutes=step); left-=step
        return cur

class SLAEngine:
    def __init__(self,calendar,rules):self.calendar,self.rules=calendar,rules
    def evaluate(self,created_at,now,priority):
        allowed=int(self.rules.get(priority,self.rules.get("medium",480)))
        elapsed=self.calendar.working_minutes_between(created_at,now)
        return {"allowed_minutes":allowed,"elapsed_minutes":elapsed,
                "warning":elapsed>=allowed*.75 and elapsed<allowed,
                "breached":elapsed>=allowed,
                "percent":round(elapsed/allowed*100,1) if allowed else 100,
                "deadline":self.calendar.add_working_minutes(created_at,allowed)}
    def apply(self,ticket,now):
        r=self.evaluate(ticket.created_at,now,ticket.priority)
        ticket.sla_minutes=r["allowed_minutes"]; ticket.sla_elapsed_minutes=r["elapsed_minutes"]
        ticket.sla_warning=r["warning"]; ticket.sla_breached=r["breached"]
        if ticket.sla_breached:
            ticket.status="sla_breached"
            ticket.escalated=True
            ticket.escalation_reason=f"SLA breach: {ticket.sla_elapsed_minutes} working minutes consumed of {ticket.sla_minutes}"
        elif ticket.sla_warning and ticket.status=="open": ticket.status="sla_warning"
        return r
