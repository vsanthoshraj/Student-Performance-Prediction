# 🛠️ Technology Stack & Design System

## 🧰 Core Stack Specifications

| Layer | Subsystem | Components & Details |
|-------|-----------|----------------------|
| **Design & Typography** | **Plus Jakarta Sans** | Modern geometric typography, HSL color tokens, glassmorphism backdrop filters |
| **Frontend UI** | HTML5, Vanilla CSS3, JS (ES6+) | Micro-animations, responsive CSS Grid layout, modal drawers |
| **Icons & Charts** | Lucide Icons, Chart.js 4.x | Vector icons, dynamic performance donut and score distribution bar charts |
| **Backend Framework**| Python 3.10+, Flask | Modular REST API routing and session management |
| **Database** | MySQL 8.0 / PyMySQL | Production database with automatic zero-downtime SQLite fallback |
| **Data Processing** | Pandas, OpenPyXL | Multi-sheet college markbook ingestion & statistical aggregation |
| **AI Integration** | Google Gemini API (`gemini-2.5-flash`) | Context-injected LLM assistant with offline rule engine fallback |
| **Email Dispatcher** | Python `smtplib`, `email.mime` | Configurable SSL/TLS SMTP email alert engine |
| **Containerization** | Docker, Docker Compose | Multi-stage image build, non-root user (UID 10001), healthchecks, layer caching |

---

## 🎨 Design System Principles

- **Typography**: Google Font **Plus Jakarta Sans** for crisp legibility and high-tech SaaS aesthetics.
- **Glassmorphism**: Subtle frosted backdrop filters (`backdrop-filter: blur(20px)`), soft border strokes, and elevated card shadows.
- **Color Token System**: Harmonious HSL colors (`--color-accent`, `--color-good`, `--color-warning`, `--color-risk`).
- **User Interactions**: Synchronized threshold range sliders, show/hide password toggles, and responsive drawers.
