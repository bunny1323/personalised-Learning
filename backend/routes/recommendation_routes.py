from flask import Blueprint, request, jsonify
from models.resource_model import Resource
from routes.quiz_routes import token_required
import os
import json
import urllib.parse

recommendation_bp = Blueprint('recommendation', __name__)

# Lazy OpenAI client
_openai_client = None
def get_client():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client


def generate_fallback(topic, learning_style):
    """Generate real, useful resources without OpenAI by constructing well-known URLs."""
    t = urllib.parse.quote(topic)
    style_label = learning_style or "Visual"

    base = [
        {
            "title": f"{topic} — Full Course for Beginners",
            "description": f"A comprehensive beginner-to-advanced video course on {topic}. Covers all major concepts with visual demonstrations.",
            "platform": "YouTube",
            "link": f"https://www.youtube.com/results?search_query={t}+full+course+for+beginners",
            "resource_type": "Video",
            "reason": f"YouTube video courses are ideal for {style_label} learners — clear visuals and structured pacing."
        },
        {
            "title": f"{topic} — Official Documentation",
            "description": f"The official, authoritative reference documentation for {topic}. Best for a deep, technical understanding.",
            "platform": "Official Docs",
            "link": f"https://www.google.com/search?q={t}+official+documentation",
            "resource_type": "Documentation",
            "reason": "Nothing beats the official docs for accuracy and depth."
        },
        {
            "title": f"{topic} Explained — FreeCodeCamp",
            "description": f"In-depth technical articles and tutorials on {topic} from freeCodeCamp, a highly trusted open-source learning platform.",
            "platform": "freeCodeCamp",
            "link": f"https://www.freecodecamp.org/news/search/?query={t}",
            "resource_type": "Article",
            "reason": f"freeCodeCamp articles are perfect for {style_label} learners who prefer structured, written explanations."
        },
        {
            "title": f"{topic} — Interactive Course",
            "description": f"Hands-on, project-based course on {topic}. Build real projects and gain practical skills.",
            "platform": "Coursera",
            "link": f"https://www.coursera.org/search?query={t}",
            "resource_type": "Course",
            "reason": "Coursera's structured courses suit learners who want guided, accredited learning paths."
        },
        {
            "title": f"Learn {topic} Interactively",
            "description": f"Interactive coding exercises and bite-sized lessons on {topic}. Great for hands-on practice.",
            "platform": "Codecademy",
            "link": f"https://www.codecademy.com/search?query={t}",
            "resource_type": "Interactive",
            "reason": f"Codecademy's interactive environment is excellent for Kinesthetic learners who learn by doing."
        },
        {
            "title": f"{topic} Tutorial — W3Schools",
            "description": f"Simple, clean reference tutorials on {topic} with live examples you can edit in the browser.",
            "platform": "W3Schools",
            "link": f"https://www.w3schools.com/search/search_result.php?search={t}",
            "resource_type": "Tutorial",
            "reason": "W3Schools' try-it-yourself examples are perfect for immediate hands-on experimentation."
        },
        {
            "title": f"{topic} Open-Source Projects on GitHub",
            "description": f"Explore real-world GitHub repositories for {topic}. Read code, contribute, and build your own projects.",
            "platform": "GitHub",
            "link": f"https://github.com/search?q={t}&type=repositories&sort=stars",
            "resource_type": "Project",
            "reason": "Studying popular open-source projects is the fastest way to see professional-grade implementations."
        },
        {
            "title": f"{topic} — Khan Academy",
            "description": f"Free, world-class educational content on {topic} from Khan Academy. Great for building foundational knowledge.",
            "platform": "Khan Academy",
            "link": f"https://www.khanacademy.org/search?page_search_query={t}",
            "resource_type": "Course",
            "reason": "Khan Academy's progressive approach suits learners who prefer to build up from fundamentals."
        },
        {
            "title": f"The Complete {topic} Roadmap",
            "description": f"Step-by-step visual roadmap showing exactly what to learn in {topic} and in what order.",
            "platform": "roadmap.sh",
            "link": f"https://roadmap.sh/search?q={t}",
            "resource_type": "Article",
            "reason": "Roadmaps give Visual learners a clear, big-picture overview of the entire learning journey."
        },
        {
            "title": f"{topic} — Stack Overflow Questions & Answers",
            "description": f"Thousands of real programming questions and expert answers on {topic} from the world's largest developer community.",
            "platform": "Stack Overflow",
            "link": f"https://stackoverflow.com/search?q={urllib.parse.quote(topic)}",
            "resource_type": "Article",
            "reason": "Stack Overflow's Q&A format helps problem-solvers learn by seeing how real issues are resolved."
        }
    ]

    # Style-based reordering
    priority = {
        "Visual":          ["Video", "Course", "Tutorial", "Interactive", "Documentation", "Article", "Project", "Article"],
        "Auditory":        ["Course", "Video", "Interactive", "Article", "Documentation", "Tutorial", "Project", "Article"],
        "Kinesthetic":     ["Interactive", "Project", "Tutorial", "Course", "Video", "Documentation", "Article", "Article"],
        "Reading/Writing": ["Documentation", "Article", "Course", "Tutorial", "Video", "Interactive", "Project", "Article"]
    }.get(style_label, [])

    def sort_key(r):
        try: return priority.index(r["resource_type"])
        except ValueError: return 99

    return sorted(base, key=sort_key)


@recommendation_bp.route('/recommend-topic', methods=['POST'])
@token_required
def recommend_topic(user_id):
    data = request.get_json()
    topic = data.get('topic')
    learning_style = data.get('learning_style', 'Visual')

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    # --- Try OpenAI first ---
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key and not api_key.startswith("your_"):
        prompt = f"""You are an expert AI tutor. Generate 10 highly curated, real learning resources for the topic: '{topic}'.
The student has a {learning_style} learning style.

Prioritise:
- Visual: YouTube videos, diagrams, infographics
- Auditory: Podcasts, lectures, audiobooks
- Reading/Writing: Blog articles, documentation, research papers
- Kinesthetic: Interactive coding platforms, GitHub repos, hands-on projects

Return ONLY a valid JSON array (no markdown) with objects containing these exact keys:
"title", "description", "platform", "link", "resource_type", "reason"

The "reason" field explains why THIS resource suits a {learning_style} learner.
Links must be real, working URLs to popular platforms (YouTube, Medium, Coursera, GitHub, etc.)."""

        try:
            response = get_client().chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You return only valid JSON arrays. No markdown, no code blocks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            resources = json.loads(raw)
            return jsonify(resources), 200
        except Exception as e:
            print(f"OpenAI error (falling back): {e}")
            # Fall through to local fallback

    # --- Fallback: curated resource engine ---
    resources = generate_fallback(topic, learning_style)
    return jsonify(resources), 200


@recommendation_bp.route('/save-resource', methods=['POST'])
@token_required
def save_resource(user_id):
    data = request.get_json()
    res_id = Resource.save(
        user_id,
        data.get('title', ''),
        data.get('link', ''),
        data.get('resource_type', 'Article'),
        data.get('platform', ''),
        data.get('description', '')
    )
    if res_id:
        return jsonify({"message": "Resource saved", "id": res_id}), 201
    return jsonify({"error": "Failed to save resource"}), 500


@recommendation_bp.route('/saved-resources', methods=['GET'])
@token_required
def get_saved_resources(user_id):
    resources = Resource.get_by_user(user_id)
    return jsonify(resources), 200


@recommendation_bp.route('/delete-resource', methods=['DELETE'])
@token_required
def delete_resource(user_id):
    data = request.get_json()
    link = data.get('link')
    if not link:
        return jsonify({"error": "Link is required"}), 400
    deleted = Resource.delete_by_link(user_id, link)
    if deleted:
        return jsonify({"message": "Resource removed"}), 200
    return jsonify({"error": "Resource not found"}), 404
