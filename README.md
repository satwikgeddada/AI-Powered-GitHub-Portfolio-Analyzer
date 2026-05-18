# AI-Powered GitHub Portfolio Analyzer 🚀

An intelligent, agent-driven platform that transforms GitHub profiles into professional, AI-analyzed portfolio dashboards and downloadable developer cards. Using Gemini 1.5 Flash and the Model Context Protocol (MCP), it provides deep insights into coding personality, technical skills, and developer impact.

![Modern Glassmorphism UI](https://img.shields.io/badge/UI-Glassmorphism-blue)
![AI Model](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-orange)
![Framework](https://img.shields.io/badge/Backend-FastAPI-green)

## ✨ Features

- **🧠 AI Personality Analysis:** Uses Gemini 1.5 Flash to analyze coding styles and project contributions to define a "Coding Personality".
- **📊 Interactive Dashboard:** Responsive Glassmorphism UI featuring developer stats, professional summaries, and technical skill charts.
- **🪪 Portfolio Cards:** Generates sleek, downloadable developer portfolio cards (as PDF or Image).
- **🤖 Agentic Workflow:** Powered by a specialized AI agent that orchestrates GitHub scraping, analysis, scoring, and card generation.
- **🔌 MCP Integration:** Implements Model Context Protocol (MCP) for tool-based interactions between the LLM and system services.
- **🌓 Dark/Light Mode:** Full support for modern theme switching with smooth transitions.

## 🛠️ Tech Stack

### Frontend
- **HTML5 & CSS3:** Modern Glassmorphism UI with responsive CSS animations.
- **JavaScript (ES6+):** Async/Await for API interactions and DOM manipulation.
- **Chart.js:** For visualizing developer skill distributions and impact.
- **html2canvas & jsPDF:** Client-side generation of downloadable portfolio cards.

### Backend
- **FastAPI:** High-performance Python web framework for the core API.
- **Google Generative AI:** Integration with Gemini 1.5 Flash for intelligent analysis.
- **FastMCP:** Used to build the Model Context Protocol server for the AI agent tools.
- **GitHub REST API:** For fetching real-time repository and user data.

### Infrastructure
- **Docker & Docker Compose:** Containerized environment for easy deployment.
- **Google Cloud Run:** Optimized for serverless deployment.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Docker & Docker Compose (Optional, for containerized run)
- GitHub Personal Access Token (for higher rate limits)
- Google Gemini API Key

### Environment Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-github-portfolio-analyzer.git
   cd ai-github-portfolio-analyzer
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Configure your keys in `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GITHUB_TOKEN=your_github_token_here (optional, but recommended)
   PORT=8000
   ```

### Running with Docker (Recommended)
The easiest way to get the app running is using Docker Compose:
```bash
docker-compose up --build
```
The application will be available at `http://localhost:8000`.

### Local Development Setup
**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Frontend:**
The frontend is served statically by the FastAPI backend. Simply visit `http://localhost:8000` once the backend is running.

## 🧠 Agentic Workflow

The `PortfolioAnalyzerAgent` follows a strict execution sequence to ensure high-quality analysis:
1. **Scrape:** Fetches user metadata, repos, languages, and contribution stats via the `scrape_github` tool.
2. **Analyze:** Gemini processes the raw data to determine coding personality and technical focus.
3. **Summarize:** Generates a professional bio tailored to the developer's strengths.
4. **Score:** Calculates a "Developer Score" based on stars, forks, and contribution consistency.
5. **Generate Card:** Combines insights into a structured format for the UI.
6. **Save:** Persists the analysis and prepares the downloadable assets.

## 📂 Project Structure

```text
ai-github-portfolio-analyzer/
├── backend/
│   ├── agent.py          # AI Agent orchestration logic
│   ├── ai_service.py     # Gemini API integration
│   ├── github_service.py # GitHub API interactions
│   ├── mcp_server.py     # MCP tool server implementation
│   ├── main.py           # FastAPI entry point
│   └── static/           # Generated portfolio cards
├── frontend/
│   ├── index.html        # Main dashboard UI
│   ├── app.js            # Frontend logic and charts
│   └── style.css         # Glassmorphism styling
├── docker-compose.yml    # Container orchestration
└── deploy.sh             # Cloud Run deployment script
```

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
