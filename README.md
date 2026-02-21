Digital Curator: AI-Powered Visual Archive
Digital Curator is a systematic solution designed to transform disorganized social media content into a structured, searchable, and intelligent library. Utilizing a WhatsApp-to-Cloud pipeline, the system leverages the Google Gemini 2.5 Flash model to extract intent and context from shared video content.


System Schematics
The platform is built on a decoupled architecture consisting of four specialized layers:

1. Ingestion Layer (Twilio & FastAPI)
Service: Twilio API for WhatsApp.
Mechanism: A FastAPI backend endpoint (running via Uvicorn).
Logic: When a user shares a URL via WhatsApp, Twilio sends a POST request to the /whatsapp webhook. The FastAPI server uses Instaloader to scrape video captions and hashtags directly from the source to bypass frontend blocks.

2. Intelligence Layer (Gemini 2.5 Flash)
Model: Google Gemini 2.5 Flash API.
Synthesis: The system passes the scraped metadata into the Gemini model. The model performs zero-shot classification to assign categorical labels and generates a concise, punchy 1-sentence summary of the video content.

3. Persistence Layer (Supabase)
Database: PostgreSQL via the Supabase REST interface.
Schema: The processed data (URL, category, summary, and raw message) is stored in a relational table for long-term retrieval and dashboard indexing.

4. Discovery Layer (Streamlit)
Interface: Streamlit Web Dashboard.
Semantic Search: A specialized UI that allows users to query their saved archive using natural language, interpreted by the Gemini model to match "vibes" or topics rather than just keywords.
UI/UX Styling: Injected CSS for a dark-mode aesthetic, custom video clipping masks to remove platform headers, and keyframe-animated discovery modules.


Technical Write-Up

The Challenge: Content Fragmentation
The "Link Graveyard" phenomenon occurs when users save high-value content on social platforms but lose the ability to retrieve it because native platforms lack sophisticated organization and search tools.
The Solution: Automated Metadata Indexing
Digital Curator solves this by implementing an AI-driven metadata excavation process. By using Instaloader to pull raw captions and feeding them into Gemini, the system provides context necessary to categorize the content automatically without the high computational cost of full video processing.


Key Technical Innovations

Asynchronous Webhook Handling: Using FastAPI, the system manages multiple incoming requests and external API calls efficiently.
Semantic Routing: Traditional keyword search is replaced with an AI-driven approach. The search functionality interprets the intent of a query—returning relevant results even if exact word matches are absent.
Responsive Video Masking: A custom CSS clipping solution for the Streamlit dashboard hides platform-specific UI elements (such as the Instagram "View Profile" header) within the iframe, creating a native-app experience.
Frictionless Ingestion: By utilizing WhatsApp as the input method, the system integrates into existing user habits with zero friction.


Installation and Deployment

Clone the Repository: git clone https://github.com/PurvaMane2005/digital_gallery.git
Install Dependencies: pip install -r requirements.txt
Configure Environment: Create a .env file containing SUPABASE_URL, SUPABASE_KEY, and GEMINI_API_KEY.
Run Ingestion Server: python app.py (FastAPI/Uvicorn)
Run Discovery Dashboard: streamlit run dashboard.py
