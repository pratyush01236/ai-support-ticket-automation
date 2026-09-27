import json,os
PROMPT="""Extract a customer support conversation into JSON with keys:
customer_name,email,phone,order_id,product,issue,evidence,sentiment,sentiment_score,severity,customer_impact,required_skill.
Use null for unknown values. Do not invent facts."""
def extract_with_gemini(text):
    key=os.getenv("GEMINI_API_KEY")
    if not key:return {}
    try:
        from google import genai
        from config import GEMINI_MODEL
        c=genai.Client(api_key=key)
        r=c.models.generate_content(model=GEMINI_MODEL,contents=PROMPT+"\nConversation:\n"+text,config={"response_mime_type":"application/json"})
        return json.loads(r.text)
    except Exception:return {}
