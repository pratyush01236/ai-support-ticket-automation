import json, os
from dotenv import load_dotenv
load_dotenv()

TIMEZONE=os.getenv("TIMEZONE","Asia/Kolkata")
BUSINESS_START=os.getenv("BUSINESS_START","09:00")
BUSINESS_END=os.getenv("BUSINESS_END","18:00")
WEEKENDS={int(x) for x in os.getenv("WEEKENDS","5,6").split(",") if x.strip()}
HOLIDAYS={x.strip() for x in os.getenv("HOLIDAYS","").split(",") if x.strip()}

def get_sla_rules():
    default={"critical":120,"high":240,"medium":480,"low":1440}
    try:
        value=json.loads(os.getenv("SLA_RULES_JSON",""))
        return {str(k).lower():int(v) for k,v in value.items()} or default
    except (ValueError,TypeError,json.JSONDecodeError):
        return default
