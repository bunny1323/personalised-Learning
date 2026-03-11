const questions = [
    {
        question: "How do you prefer to learn new information?",
        options: [
            { text: "Watching diagrams and videos",        style: "Visual" },
            { text: "Listening to lectures or podcasts",   style: "Auditory" },
            { text: "Practising hands-on activities",      style: "Kinesthetic" },
            { text: "Reading notes or articles",           style: "Reading/Writing" }
        ]
    },
    {
        question: "When solving a problem, what helps you most?",
        options: [
            { text: "Visualising the solution with diagrams",  style: "Visual" },
            { text: "Talking through the options with someone", style: "Auditory" },
            { text: "Building a prototype and experimenting",  style: "Kinesthetic" },
            { text: "Writing out all the steps systematically", style: "Reading/Writing" }
        ]
    },
    {
        question: "What is your ideal study environment?",
        options: [
            { text: "Clean space with visual aids everywhere", style: "Visual" },
            { text: "Quiet space to listen to background music", style: "Auditory" },
            { text: "Active space where I can move around", style: "Kinesthetic" },
            { text: "Library with plenty of reference books", style: "Reading/Writing" }
        ]
    },
    {
        question: "How do you best remember someone's name?",
        options: [
            { text: "Visualising their face or business card", style: "Visual" },
            { text: "Repeating the name out loud a few times", style: "Auditory" },
            { text: "Connecting it to a unique gesture or action", style: "Kinesthetic" },
            { text: "Writing it down somewhere", style: "Reading/Writing" }
        ]
    },
    {
        question: "In a class, you prefer:",
        options: [
            { text: "Presentations with charts and graphics", style: "Visual" },
            { text: "Group discussions and conversations", style: "Auditory" },
            { text: "Lab sessions and practical workshops", style: "Kinesthetic" },
            { text: "Detailed lecture notes and handouts", style: "Reading/Writing" }
        ]
    },
    {
        question: "To learn a new game or skill, you would:",
        options: [
            { text: "Watch a tutorial video first", style: "Visual" },
            { text: "Ask someone to explain the rules", style: "Auditory" },
            { text: "Just start playing and learn as you go", style: "Kinesthetic" },
            { text: "Read the instruction manual carefully", style: "Reading/Writing" }
        ]
    }
];

const letters = ['A','B','C','D'];
let currentQ = 0;
let responses = [];

function initQuiz() {
    const content = document.getElementById('quizContent');
    content.innerHTML = questions.map((q, qi) => `
        <div class="glass-card question-card ${qi === 0 ? 'active' : ''}" id="q${qi}">
            <div class="q-number">Question ${qi + 1} of ${questions.length}</div>
            <div class="q-text">${q.question}</div>
            <div class="options-grid">
                ${q.options.map((opt, oi) => `
                    <button class="option-btn" onclick="pick('${opt.style}','${escQ(q.question)}','${escQ(opt.text)}')">
                        <span class="opt-letter">${letters[oi]}</span>
                        ${opt.text}
                    </button>`).join('')}
            </div>
        </div>
    `).join('');
    updateProgress();
}

function escQ(s) { return s.replace(/'/g, "\\'"); }

function pick(style, question, answer) {
    responses.push({ question, answer, style });
    currentQ++;
    const pct = (currentQ / questions.length) * 100;
    document.getElementById('progressFill').style.width = `${pct}%`;
    document.getElementById('progressLabel').innerText = `${currentQ} / ${questions.length}`;

    if (currentQ < questions.length) {
        document.querySelector('.question-card.active').classList.remove('active');
        document.getElementById(`q${currentQ}`).classList.add('active');
    } else {
        submitQuiz();
    }
}

function updateProgress() {
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('progressLabel').innerText = `0 / ${questions.length}`;
}

async function submitQuiz() {
    document.getElementById('quizContent').style.display = 'none';
    document.getElementById('quizResult').style.display = 'flex';
    document.getElementById('quizResult').style.flexDirection = 'column';
    document.getElementById('quizResult').style.alignItems = 'center';

    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`${API_URL}/quiz/submit-quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ responses })
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('detectedStyle').innerText = data.learning_style;
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            user.learning_style = data.learning_style;
            localStorage.setItem('user', JSON.stringify(user));
        } else {
            document.getElementById('detectedStyle').innerText = 'Error — please retry';
        }
    } catch {
        document.getElementById('detectedStyle').innerText = 'Server not responding';
    }
}

checkAuth();
initQuiz();
