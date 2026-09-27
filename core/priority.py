S={"low":1,"medium":2,"high":3,"critical":4}
N={"positive":0,"neutral":0,"negative":1,"very_negative":2}
I={"individual":0,"multiple":1,"business_wide":2,"safety":3}

def calculate_priority(t,sla_remaining=None):
    score=S.get(t.severity,2)+N.get(t.sentiment,0)+I.get(t.customer_impact,0)
    if t.waiting_minutes>=60: score+=1
    if t.waiting_minutes>=240: score+=1
    if sla_remaining is not None:
        if sla_remaining<=0: score+=3
        elif sla_remaining<=max(t.sla_minutes*.25,1): score+=2
        elif sla_remaining<=max(t.sla_minutes*.5,1): score+=1
    t.priority="critical" if score>=8 else "high" if score>=6 else "medium" if score>=4 else "low"
    return t.priority
