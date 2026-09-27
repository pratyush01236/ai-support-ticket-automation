import re
from difflib import SequenceMatcher

STOP={"the","a","an","is","are","to","of","for","and","my","i","it","this"}

def words(s):return {x for x in re.findall(r"[a-z0-9]+",s.lower()) if x not in STOP}
def similarity(a,b):
    x=" ".join(sorted(words(a.issue))); y=" ".join(sorted(words(b.issue)))
    text=SequenceMatcher(None,x,y).ratio()
    order=1 if a.order_id and a.order_id==b.order_id else 0
    product=1 if a.product and b.product and a.product.lower()==b.product.lower() else 0
    return .55*text+.30*order+.15*product

def find_duplicate(ticket,existing,threshold=.78):
    for other in existing:
        if other.ticket_id==ticket.ticket_id:continue
        score=similarity(ticket,other)
        if score>=threshold:
            ticket.duplicate_of=other.ticket_id; return other.ticket_id,score
    return None,0

def group_related(ticket,existing,threshold=.48):
    ticket.related_ticket_ids=[x.ticket_id for x in existing if x.ticket_id!=ticket.ticket_id and ticket.duplicate_of!=x.ticket_id and similarity(ticket,x)>=threshold]
    return ticket.related_ticket_ids

def separate_unrelated(ticket,existing,threshold=.30):
    ticket.unrelated_ticket_ids=[x.ticket_id for x in existing if x.ticket_id!=ticket.ticket_id and similarity(ticket,x)<threshold]
    return ticket.unrelated_ticket_ids
