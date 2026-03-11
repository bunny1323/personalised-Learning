# AI-Based Personalized Learning Recommendation System

A modern SaaS platform that uses AI to provide tailored learning resources based on a student's unique learning style.

## 🚀 Features
- **AI Personalization**: Powered by GPT-3.5 to curate resources (YouTube, Articles, Labs).
- **Learning Style Quiz**: 6-question assessment to detect your style (Visual, Auditory, etc.).
- **Modern UI**: Glassmorphism design, dark/light mode, and smooth transitions.
- **Progress Tracking**: Streak counter and topic history.
- **Saved Resources**: Bookmark your favorite materials to your PostgreSQL database.

## 🛠️ Tech Stack
- **Frontend**: Vanilla JS, CSS3 (Glassmorphism), HTML5.
- **Backend**: Python/Flask.
- **Database**: PostgreSQL.
- **AI**: OpenAI API.

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.8+
- PostgreSQL installed and running.
- OpenAI API Key.

### 2. Backend Setup
1. Navigate to the `backend/` directory.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure `.env` file:
   - Create a database called `learning_platform` in PostgreSQL.
   - Update `DB_PASS` and `OPENAI_API_KEY` in `backend/.env`.

### 3. Database Initialization
Run the initialization script:
```bash
python database/db.py
```

### 4. Run the Application
1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open `frontend/index.html` in your browser.

## 📖 Application Flow
1. **Landing**: Professional hero section.
2. **Auth**: Register and Login with JWT security.
3. **Quiz**: Determine if you are Visual, Auditory, Reading, or Kinesthetic.
4. **Dashboard**: Search for any topic and get AI-explained recommendations.
