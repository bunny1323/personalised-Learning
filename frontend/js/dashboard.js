const user = JSON.parse(localStorage.getItem('user'));
const token = localStorage.getItem('token');

// ── Auth guard ──
checkAuth();

// ── Populate sidebar ──
if (user) {
    document.getElementById('userName').innerText = user.name || 'Learner';
    document.getElementById('userAvatar').innerText = (user.name || 'U').charAt(0).toUpperCase();
    document.getElementById('userStyle').innerText = user.learning_style ? `${user.learning_style} Learner` : 'Style Pending';
    const streak = user.streak_count || 1;
    document.getElementById('streakCount').innerText = `${streak} Day${streak !== 1 ? 's' : ''}`;
}

// ── Restore theme ──
const themeToggle = document.getElementById('themeToggle');
if (localStorage.getItem('theme') === 'light') {
    document.body.classList.add('light-mode');
    themeToggle.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
}
themeToggle.addEventListener('click', () => {
    const isLight = document.body.classList.toggle('light-mode');
    themeToggle.innerHTML = isLight
        ? '<i class="fas fa-sun"></i> Light Mode'
        : '<i class="fas fa-moon"></i> Dark Mode';
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
});

// ── Enter key ──
document.getElementById('topicInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') handleSearch();
});

// ── Search ──
async function handleSearch() {
    const topic = document.getElementById('topicInput').value.trim();
    if (!topic) { showToast('Please enter a topic to search.', '#f97316'); return; }

    showLoading(true);
    try {
        const res = await fetch(`${API_URL}/recommendation/recommend-topic`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ topic, learning_style: user?.learning_style || 'Visual' })
        });
        const data = await res.json();
        if (res.ok) {
            renderRecs(data, topic);
            updateHistory(topic);
        } else {
            showToast(data.error || 'Failed to get recommendations', '#ef4444');
        }
    } catch (err) {
        console.error(err);
        showToast('Cannot reach the server. Is it running?', '#ef4444');
    } finally {
        showLoading(false);
    }
}

function renderRecs(resources, topic) {
    const section = document.getElementById('recsSection');
    const grid = document.getElementById('recsGrid');
    document.getElementById('recsHeading').innerText = `Results for "${topic}"`;
    document.getElementById('recsCount').innerText = `${resources.length} resources`;
    section.style.display = 'block';
    grid.innerHTML = '';
    resources.forEach((r, i) => {
        const card = buildCard(r, true);
        card.style.animationDelay = `${i * 0.05}s`;
        grid.appendChild(card);
    });
    section.scrollIntoView({ behavior: 'smooth' });
}

function buildCard(r, saveable) {
    const typeKey = (r.resource_type || r.type || 'article').toLowerCase().split(/[\s_]/)[0];
    const div = document.createElement('div');
    div.className = 'glass-card resource-card animate-fade-in';
    div.innerHTML = `
        <div class="card-top">
            <span class="badge badge-${typeKey}">${r.resource_type || r.type || 'Resource'}</span>
            <span class="card-platform">${r.platform || ''}</span>
        </div>
        <div class="card-title">${r.title}</div>
        <div class="card-desc">${r.description || ''}</div>
        ${r.reason ? `<div class="card-reason">💡 <strong>Why this fits:</strong> ${r.reason}</div>` : ''}
        <div class="card-actions">
            <a href="${r.link}" target="_blank" rel="noopener" class="btn-primary">
                Open <i class="fas fa-external-link-alt"></i>
            </a>
            ${saveable
                ? `<button class="btn-icon" title="Save resource" onclick="saveResource(this, ${JSON.stringify(r).replace(/"/g, '&quot;')})">
                       <i class="fas fa-bookmark"></i>
                   </button>`
                : `<button class="btn-icon danger" title="Remove" data-link="${r.link}"
                       onclick="unsave(this)" style="color:#f87171;">
                       <i class="fas fa-trash"></i>
                   </button>`
            }
        </div>
    `;
    return div;
}

// ── Save resource ──
async function saveResource(btn, r) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    try {
        const res = await fetch(`${API_URL}/recommendation/save-resource`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(r)
        });
        if (res.ok) {
            btn.innerHTML = '<i class="fas fa-check" style="color:#10b981;"></i>';
            showToast('Saved! ✓', '#10b981');
            loadSaved();
        } else {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-bookmark"></i>';
        }
    } catch { btn.disabled = false; btn.innerHTML = '<i class="fas fa-bookmark"></i>'; }
}

// ── Unsave ──
async function unsave(btn) {
    const link = btn.getAttribute('data-link');
    try {
        const res = await fetch(`${API_URL}/recommendation/delete-resource`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ link })
        });
        if (res.ok) {
            btn.closest('.resource-card').remove();
            showToast('Removed.', '#6366f1');
            checkSavedEmpty();
            updateSavedCount();
        }
    } catch (e) { console.error(e); }
}

// ── Load saved resources ──
async function loadSaved() {
    try {
        const res = await fetch(`${API_URL}/recommendation/saved-resources`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok) {
            const grid = document.getElementById('savedGrid');
            grid.innerHTML = '';
            if (!data.length) { renderEmpty(grid); return; }
            data.forEach(r => grid.appendChild(buildCard(r, false)));
            document.getElementById('savedCount').innerText = data.length;
        }
    } catch (e) { console.error(e); }
}

function renderEmpty(grid) {
    grid.innerHTML = `
        <div class="empty-state">
            <i class="fas fa-bookmark"></i>
            <p>Nothing saved yet</p>
            <small>Search a topic above and bookmark your favourites</small>
        </div>`;
    document.getElementById('savedCount').innerText = '0';
}

function checkSavedEmpty() {
    const grid = document.getElementById('savedGrid');
    if (!grid.querySelector('.resource-card')) renderEmpty(grid);
}

function updateSavedCount() {
    const n = document.getElementById('savedGrid').querySelectorAll('.resource-card').length;
    document.getElementById('savedCount').innerText = n;
}

function updateHistory(topic) {
    let h = JSON.parse(localStorage.getItem('topicHistory') || '[]');
    if (!h.includes(topic)) { h.unshift(topic); if (h.length > 20) h.pop(); }
    localStorage.setItem('topicHistory', JSON.stringify(h));
    document.getElementById('topicCount').innerText = h.length;
}

// ── Toast ──
function showToast(msg, color = '#a855f7') {
    const el = document.getElementById('toast');
    el.innerText = msg;
    el.style.cssText = `
        display:flex; background:${color}; color:white;
        position:fixed; bottom:2rem; right:2rem; z-index:99999;
        padding:12px 20px; border-radius:14px; font-weight:600;
        font-size:0.88rem; box-shadow:0 8px 30px rgba(0,0,0,0.4);
        animation:fadeInUp 0.3s ease;
    `;
    clearTimeout(el._t);
    el._t = setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function showLoading(v) {
    document.getElementById('loadingOverlay').style.display = v ? 'flex' : 'none';
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

// ── Init ──
loadSaved();
document.getElementById('topicCount').innerText = JSON.parse(localStorage.getItem('topicHistory') || '[]').length;
