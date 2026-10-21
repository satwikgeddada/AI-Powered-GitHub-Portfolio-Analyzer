// API Configuration
const API_BASE_URL = 'https://ai-powered-github-portfolio-analyzer.onrender.com/';
// DOM Elements
const analyzeBtn = document.getElementById('analyze-btn');
const usernameInput = document.getElementById('username-input');
const resultsSection = document.getElementById('results-section');
const loadingSkeleton = document.getElementById('loading-skeleton');
const themeToggle = document.getElementById('theme-toggle');
const errorContainer = document.getElementById('error-container');
const errorMessage = document.getElementById('error-message');
const compareBtn = document.getElementById('compare-btn');
const compareResultsDiv = document.getElementById('compare-results');

// Chart Instances
let langsChart, starsChart, specChart, compChart;
let lastAnalysisData = null;
let lastComparisonData = null;

// Theme Logic
const currentTheme = localStorage.getItem('theme') || 'dark';
document.documentElement.setAttribute('data-theme', currentTheme);
themeToggle.textContent = currentTheme === 'dark' ? '🌙' : '☀️';

themeToggle.addEventListener('click', () => {
    const theme = document.documentElement.getAttribute('data-theme');
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    themeToggle.textContent = newTheme === 'dark' ? '🌙' : '☀️';
    
    // Update charts on theme change
    if (resultsSection.classList.contains('hidden') === false && lastAnalysisData) {
        renderCharts(lastAnalysisData);
    }
    if (compareResultsDiv.classList.contains('hidden') === false && lastComparisonData) {
        renderComparisonChart(lastComparisonData);
    }
});

function showError(msg) {
    errorMessage.textContent = msg;
    errorContainer.classList.remove('hidden');
    setTimeout(() => errorContainer.classList.add('hidden'), 5000);
}

// ---------------------------------------------------------
// Profile Analysis Logic
// ---------------------------------------------------------

analyzeBtn.addEventListener('click', async () => {
    const username = usernameInput.value.trim();
    if (!username) return showError('Please enter a GitHub username');

    const theme = document.documentElement.getAttribute('data-theme') || 'dark';

    analyzeBtn.disabled = true;
    analyzeBtn.querySelector('.btn-text').classList.add('hidden');
    analyzeBtn.querySelector('.loader').classList.remove('hidden');
    loadingSkeleton.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    errorContainer.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, theme })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Analysis failed');

        lastAnalysisData = data;
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.querySelector('.btn-text').classList.remove('hidden');
        analyzeBtn.querySelector('.loader').classList.add('hidden');
        loadingSkeleton.classList.add('hidden');
    }
});

function renderCharts(data) {
    const { profile } = data;
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#475569';
    const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)';

    // Languages Chart
    const langCtx = document.getElementById('languages-chart').getContext('2d');
    if (langsChart) langsChart.destroy();
    langsChart = new Chart(langCtx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(profile.language_percentages),
            datasets: [{
                data: Object.values(profile.language_percentages),
                backgroundColor: ['#38bdf8', '#818cf8', '#6366f1', '#a855f7', '#ec4899'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { color: textColor } } }
        }
    });

    // Stars Bar Chart
    const starsCtx = document.getElementById('stars-chart').getContext('2d');
    if (starsChart) starsChart.destroy();
    starsChart = new Chart(starsCtx, {
        type: 'bar',
        data: {
            labels: profile.top_repositories.map(r => r.name.substring(0, 10)),
            datasets: [{ label: 'Stars', data: profile.top_repositories.map(r => r.stars), backgroundColor: '#38bdf8' }]
        },
        options: {
            responsive: true,
            scales: {
                y: { grid: { color: gridColor }, ticks: { color: textColor } },
                x: { ticks: { color: textColor } }
            }
        }
    });

    // Radar Specialization
    const specCtx = document.getElementById('specialization-chart').getContext('2d');
    if (specChart) specChart.destroy();
    const specLabels = ['Backend', 'Frontend', 'AI/ML', 'Mobile', 'DevOps'];
    const specData = specLabels.map(l => profile.specialization_scores ? profile.specialization_scores[l] : 50);

    specChart = new Chart(specCtx, {
        type: 'radar',
        data: {
            labels: specLabels,
            datasets: [{ 
                data: specData, 
                backgroundColor: isDark ? 'rgba(56, 189, 248, 0.2)' : 'rgba(14, 165, 233, 0.2)', 
                borderColor: isDark ? '#38bdf8' : '#0ea5e9',
                pointBackgroundColor: isDark ? '#38bdf8' : '#0ea5e9'
            }]
        },
        options: {
            scales: { 
                r: { 
                    angleLines: { color: gridColor }, 
                    grid: { color: gridColor }, 
                    pointLabels: { color: textColor, font: { size: 12, weight: '600' } }, 
                    min: 0, 
                    max: 100,
                    ticks: { display: false }
                } 
            },
            plugins: { legend: { display: false } },
            animation: { duration: 1000, easing: 'easeOutQuart' }
        }
    });
}

function displayResults(data) {
    const { profile, personality, summary, score, guidance, card_url } = data;
    resultsSection.classList.remove('hidden');

    document.getElementById('user-avatar').src = profile.avatar;
    document.getElementById('user-name').textContent = profile.name;
    document.getElementById('user-handle').textContent = `@${profile.username}`;
    document.getElementById('dev-score').textContent = score.score;
    document.getElementById('personality-desc').textContent = personality.developer_personality;
    document.getElementById('professional-summary').textContent = summary.linkedin_summary;
    document.getElementById('stat-stars').textContent = profile.total_stars;
    document.getElementById('stat-repos').textContent = profile.public_repos;
    document.getElementById('stat-followers').textContent = profile.followers;

    const strengthsList = document.getElementById('strengths-list');
    strengthsList.innerHTML = personality.top_strengths.map(s => `<li>${s}</li>`).join('');
    const weaknessesList = document.getElementById('weaknesses-list');
    weaknessesList.innerHTML = personality.weaknesses.map(w => `<li>${w}</li>`).join('');

    renderCharts(data);

    if (card_url) {
        const fullUrl = `${API_BASE_URL}${card_url}`;
        fetch(fullUrl).then(res => res.text()).then(html => {
            document.getElementById('hidden-card-capture').innerHTML = html;
            document.getElementById('card-preview-container').innerHTML = `<div style="transform: scale(0.5); transform-origin: top center;">${html}</div>`;
        });
        document.getElementById('download-png-btn').onclick = () => downloadAsPNG(profile.username);
        document.getElementById('download-pdf-btn').onclick = () => downloadAsPDF(profile.username);
    }

    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// ---------------------------------------------------------
// Benchmarking Logic
// ---------------------------------------------------------

function renderComparisonChart(data) {
    const ctx = document.getElementById('comparison-chart').getContext('2d');
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#475569';

    if (compChart) compChart.destroy();
    compChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Stars', 'Followers', 'Repos'],
            datasets: [
                { label: data.user1.name, data: [data.user1.total_stars, data.user1.followers, data.user1.public_repos], backgroundColor: '#38bdf8' },
                { label: data.user2.name, data: [data.user2.total_stars, data.user2.followers, data.user2.public_repos], backgroundColor: '#818cf8' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { ticks: { color: textColor } }, x: { ticks: { color: textColor } } },
            plugins: { legend: { labels: { color: textColor } } }
        }
    });
}

compareBtn.addEventListener('click', async () => {
    const u1 = document.getElementById('user1-input').value.trim();
    const u2 = document.getElementById('user2-input').value.trim();
    if (!u1 || !u2) return showError('Enter two usernames');

    compareBtn.disabled = true;
    compareBtn.textContent = 'Comparing...';
    compareResultsDiv.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/compare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user1: u1, user2: u2 })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Comparison failed');

        document.getElementById('comp-avatar1').src = data.user1.avatar;
        document.getElementById('comp-name1').textContent = data.user1.name;
        document.getElementById('comp-avatar2').src = data.user2.avatar;
        document.getElementById('comp-name2').textContent = data.user2.name;

        ['total_stars', 'followers', 'public_repos'].forEach(m => {
            const val1 = data.user1[m];
            const val2 = data.user2[m];
            const id = m === 'total_stars' ? 'stars' : m === 'public_repos' ? 'repos' : m;
            const el1 = document.getElementById(`comp-${id}1`);
            const el2 = document.getElementById(`comp-${id}2`);
            el1.textContent = val1; el2.textContent = val2;
            el1.classList.toggle('winner-val', val1 > val2);
            el2.classList.toggle('winner-val', val2 > val1);
        });

        compareResultsDiv.classList.remove('hidden');
        renderComparisonChart(data);
        compareResultsDiv.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
        showError(err.message);
    } finally {
        compareBtn.disabled = false;
        compareBtn.textContent = 'Compare Developers';
    }
});

// ---------------------------------------------------------
// Export Logic
// ---------------------------------------------------------

async function downloadAsPNG(username) {
    const element = document.getElementById('hidden-card-capture').firstElementChild;
    if (!element) return showError('Card element not found. Please analyze again.');
    
    const canvas = await html2canvas(element, { 
        useCORS: true, 
        backgroundColor: null,
        scale: 2 // Higher quality
    });
    
    const link = document.createElement('a');
    link.download = `${username}-card.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
}

async function downloadAsPDF(username) {
    const element = document.getElementById('hidden-card-capture').firstElementChild;
    if (!element) return showError('Card element not found. Please analyze again.');

    // Temporary style for better capture
    const originalStyle = element.style.cssText;
    element.style.boxShadow = 'none'; // Avoid weird shadow artifacts in PDF
    
    try {
        const canvas = await html2canvas(element, { 
            useCORS: true, 
            backgroundColor: '#0f172a', // Match dark theme background
            scale: 2
        });
        
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF({ 
            orientation: 'p', 
            unit: 'px', 
            format: [canvas.width, canvas.height] 
        });
        
        pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, canvas.width, canvas.height);
        pdf.save(`${username}-card.pdf`);
    } catch (err) {
        console.error('PDF Export Error:', err);
        showError('Failed to generate PDF. Try PNG instead.');
    } finally {
        element.style.cssText = originalStyle;
    }
}
