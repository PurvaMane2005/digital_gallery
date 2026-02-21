import os
import json
import httpx
import uvicorn
import re
import instaloader
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# --- Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

def get_hackathon_metadata(url):
    """
    Hackathon-grade scraper. Uses Instaloader to bypass Instagram's 
    frontend blocks and extract the exact reel caption.
    """
    try:
        # Extract the unique shortcode (e.g., 'C8q_xyz' from the URL)
        match = re.search(r"instagram\.com/(?:[^/]+/)?(?:reel|p)/([^/?]+)", url)
        if not match:
            return None
            
        shortcode = match.group(1)
        
        # Use Instaloader to pull metadata instantly
        L = instaloader.Instaloader(quiet=True)
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        return f"Caption: {post.caption}\nHashtags: {post.caption_hashtags}"
        
    except Exception as e:
        print(f"Instaloader failed: {e}")
        return None

def ask_gemini_with_context(message_text, scraped_text, url):
    """Feeds the scraped data to Gemini and logs EXACTLY what goes wrong."""
    
    prompt = (
        f"You are a smart categorizer for a video archiving bot.\n"
        f"Here is the raw text scraped from the Instagram reel:\n"
        f"--- START SCRAPED DATA ---\n"
        f"{scraped_text if scraped_text else 'No data scraped.'}\n"
        f"--- END SCRAPED DATA ---\n\n"
        f"URL: {url}\n\n"
        "RULES:\n"
        "1. Read the scraped data and assign the most suitable CATEGORY from this list: "
        "[Science, Animals, Fitness, Coding, Food, Design, Travel, Other].\n"
        "2. Write a short, punchy 1-sentence SUMMARY of what the video is about.\n"
        "3. You MUST output a valid JSON object matching this exact schema using DOUBLE QUOTES:\n"
        '{"category": "...", "summary": "...", "action_type": "URL", "action_data": "..."}'
    )

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": safety_settings,
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        print("🧠 Sending data to Gemini API...")
        # 🔥 Bumped timeout to 30s. Sometimes Gemini is just slow and causes a crash.
        response = httpx.post(MODEL_URL, json=payload, timeout=30.0)
        res_json = response.json()
        
        # 🔥 DEBUG: This will print EXACTLY what Gemini sends back to your terminal
        print(f"\n🤖 GEMINI RAW RESPONSE:\n{json.dumps(res_json, indent=2)}\n")
        
        if 'candidates' in res_json:
            raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        else:
            print("⚠️ ERROR: No 'candidates' found! Look at the RAW RESPONSE above to see why.")
            return {"category": "Error", "summary": "API Rejected Request. Check Terminal.", "action_type": "URL", "action_data": url}
            
    except Exception as e:
        # 🔥 DEBUG: This will catch timeouts or strict JSON parsing errors
        print(f"\n🔥 AI/JSON CRASH EXCEPTION: {str(e)}\n")
        return {"category": "Crash", "summary": f"System Error: {str(e)}", "action_type": "URL", "action_data": url}

def save_to_supabase(data, url, raw_msg):
    """Saves the categorized data to your Supabase database."""
    headers = {
        "apikey": SUPABASE_KEY, 
        "Authorization": f"Bearer {SUPABASE_KEY}", 
        "Content-Type": "application/json"
    }
    payload = {
        "url": url, 
        "category": data.get('category'), 
        "summary": data.get('summary'),
        "action_type": data.get('action_type'), 
        "action_data": data.get('action_data'),
        "raw_message": raw_msg
    }
    return httpx.post(f"{SUPABASE_URL}/rest/v1/saves", json=payload, headers=headers)

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Listens for incoming messages from Twilio."""
    form_data = await request.form()
    body = form_data.get('Body', '').strip()
    twiml = MessagingResponse()

    if "http" in body:
        url = next((w for w in body.split() if w.startswith("http")), None)
        
        # 1. Scrape the caption
        scraped_text = get_hackathon_metadata(url)
        print(f" SCRAPED DATA: {scraped_text}") 
        
        # 2. Categorize with Gemini
        extracted = ask_gemini_with_context(body, scraped_text, url)
        
        # 3. Save to database
        save_to_supabase(extracted, url, body)
        
        # 4. Format the final WhatsApp reply with Tags and Descriptions
        reply = (
            f"🏷️ *Tag:* {extracted.get('category', 'Other')}\n"
            f"📝 *Summary:* {extracted.get('summary', 'Saved successfully.')}\n"
        )
        twiml.message(reply)
    else:
        twiml.message("Please send a valid link!")

    return Response(content=str(twiml), media_type="application/xml")

if __name__ == "__main__":
    # reload=True automatically updates the server when you hit save!
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)