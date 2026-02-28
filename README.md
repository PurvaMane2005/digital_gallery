
# Digital Curator: AI-Powered Visual Archive

Digital Curator is a systematic solution designed to transform disorganized social media content into a structured, searchable, and intelligent library. Utilizing a WhatsApp-to-Cloud pipeline, the system leverages the **Google Gemini 2.5 Flash** model to extract intent and context from shared video content.

---

## System Schematics

The platform is built on a decoupled architecture consisting of four specialized layers:



### 1. Ingestion Layer (Twilio & FastAPI)
* **Service:** Twilio API for WhatsApp.
* **Mechanism:** A FastAPI backend endpoint (running via Uvicorn).
* **Logic:** When a user shares a URL via WhatsApp, Twilio sends a POST request to the `/whatsapp` webhook. The FastAPI server uses **Instaloader** to scrape video captions and hashtags directly from the source to bypass frontend blocks.

### 2. Intelligence Layer (Gemini 2.5 Flash)
* **Model:** Google Gemini 2.5 Flash API.
* **Synthesis:** The system passes the scraped metadata into the Gemini model. The model performs zero-shot classification to assign categorical labels and generates a concise, punchy 1-sentence summary of the video content.

### 3. Persistence Layer (Supabase)
* **Database:** PostgreSQL via the Supabase REST interface.
* **Schema:** The processed data (URL, category, summary, and raw message) is stored in a relational table for long-term retrieval and dashboard indexing.

### 4. Discovery Layer (Streamlit)
* **Interface:** Streamlit Web Dashboard.
* **Semantic Search:** A specialized UI that allows users to query their saved archive using natural language, interpreted by the Gemini model to match "vibes" or topics rather than just keywords.
* **UI/UX Styling:** Injected CSS for a dark-mode aesthetic, custom video clipping masks to remove platform headers, and keyframe-animated discovery modules.

<img width="1024" height="1024" alt="System_diagram_hackthethread" src="https://github.com/user-attachments/assets/995b0f56-0cca-4919-a2e8-6c9fc260698c" />

---

## Technical Write-Up

### The Challenge: Content Fragmentation
The "Link Graveyard" phenomenon occurs when users save high-value content on social platforms but lose the ability to retrieve it because native platforms lack sophisticated organization and search tools.

### The Solution: Automated Metadata Indexing
Digital Curator solves this by implementing an AI-driven metadata excavation process. By using Instaloader to pull raw captions and feeding them into Gemini, the system provides context necessary to categorize the content automatically without the high computational cost of full video processing.

### Key Technical Innovations
* **Asynchronous Webhook Handling:** Using FastAPI, the system manages multiple incoming requests and external API calls efficiently.
* **Semantic Routing:** Traditional keyword search is replaced with an AI-driven approach that interprets query intent.
* **Responsive Video Masking:** A custom CSS clipping solution for the Streamlit dashboard hides platform-specific UI elements within the iframe.
* **Frictionless Ingestion:** Utilizes WhatsApp as the primary input method to integrate into existing user habits with zero friction.

---

## AI Scoring and Verification Engine

> **Note:** These features were implemented post-recording. Core logic and outputs are detailed below.

The system implements a multi-stage evaluation pipeline to ensure data integrity. To mitigate AI hallucinations and handle metadata scraping limitations, a hybrid scoring engine combines probabilistic AI inference with deterministic metadata verification.

### Hybrid Confidence Scoring

Every ingested link is assigned a Confidence Score based on **Data Density** (scraped text volume) and **Model Certainty** (LLM probability).



```python
def calculate_confidence_score(scraped_text, ai_certainty):
    """
    Calculates a final confidence percentage.
    Final Score = (Evidence * 0.6) + (AI Certainty * 0.4)
    """
    # 1. Evaluate Evidence (Data Density)
    evidence_score = min(1.0, len(scraped_text) / 500) if scraped_text else 0.0
    
    # 2. Weighted Calculation
    final_score = (evidence_score * 0.6) + (ai_certainty * 0.4)
    
    return round(final_score * 100, 2)

```

### Dynamic Discovery and Taxonomy Validation

The system utilizes **Zero-Shot Dynamic Tagging**, allowing the platform to adapt to emerging trends without a fixed category list.

```python
def generate_dynamic_tags(scraped_text):
    """
    Instructional prompt for Gemini to generate context-aware labels.
    """
    prompt = (
        f"Analyze this content: {scraped_text}\n"
        "1. Generate 1-2 concise category tags.\n"
        "2. Provide a 1-sentence summary.\n"
        "3. Rate certainty in these tags from 0.0 to 1.0.\n"
    )
    # Returns structured JSON with discovered tags and certainty

```

### Post-Inference Accuracy Check

A secondary heuristic cross-references AI tags against domain-specific keywords for "ground truth" verification.

```python
KEYWORD_MAP = {
    "Coding": ["python", "code", "dev", "api", "software", "terminal"],
    "Food": ["recipe", "cook", "chef", "delicious", "eat", "ingredients"],
    "Fitness": ["gym", "workout", "protein", "training", "reps"]
}

def verify_accuracy(category, text):
    if not text: 
        return 0.0
    
    valid_keywords = KEYWORD_MAP.get(category, [])
    matches = [word for word in valid_keywords if word in text.lower()]
    
    return 1.0 if len(matches) > 0 else 0.5

```

### Performance Metrics for Dashboard UI

* **Verified (80-100%):** High metadata density and confirmed keyword matches.
* **Uncertain (40-79%):** Valid AI inference but limited supporting metadata.
* **Failed/Blocked (0-39%):** Scraper blocked; categorization based on URL context only.

<img width="1792" height="1369" alt="Screenshot_Dashboard" src="https://github.com/user-attachments/assets/d02cd733-93c1-403b-a26b-260ee67c9d91" />

---

## Installation and Deployment

1. **Clone the Repository:**

```bash
git clone [https://github.com/PurvaMane2005/digital_gallery.git](https://github.com/PurvaMane2005/digital_gallery.git)

```

2. **Install Dependencies:**

```bash
pip install -r requirements.txt

```

3. **Configure Environment:**
Create a `.env` file containing:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_api_key

```

4. **Run Ingestion Server:**

```bash
python app.py

```

5. **Run Discovery Dashboard:**

```bash
streamlit run dashboard.py

```

---

### Project Preview

https://github.com/user-attachments/assets/dff7a309-7c9d-4d97-9d22-f4bcc2d9bb78


