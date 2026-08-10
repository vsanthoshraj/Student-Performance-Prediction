# 🛠️ Technology Stack & Design System

## 🧰 Core Stack Specifications

| Subsystem | Components | Details |
|-----------|------------|---------|
| **Frontend UI** | HTML5, Vanilla CSS3, JavaScript (ES6+) | Custom glassmorphism design tokens, micro-animations, responsive layout |
| **Icons & Charts** | Lucide Icons, Chart.js 4.x | Dynamic donut & bar charts, vector icons |
| **Backend API** | Python 3.10+, Flask | Modular REST API routing structure |
| **Database** | MySQL 8.0 / PyMySQL | Primary persistent store with transparent **SQLite fallback** |
| **Data Processing**| Pandas, OpenPyXL, NumPy | Multi-sheet Excel extraction & statistical aggregation |
| **AI Integration** | Google Gemini API (`gemini-2.5-flash`) | Context-injected assistant + local NLP fallback engine |
| **Email Engine** | Python `smtplib`, `email.mime` | Configurable TLS/SSL SMTP alert dispatcher |
| **Containerization**| Docker, Docker Compose | Multi-stage image build & orchestrated MySQL stack |

---

## 🎨 Design System Principles

- **Palette**: Sleek dark/light Apple aesthetic using tailored HSL color variables (`--color-accent`, `--color-risk`, `--color-good`, `--color-warning`).
- **Typography**: Modern system font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`).
- **Glassmorphism**: Subtle backdrop filters (`backdrop-filter: blur(20px)`), frosted glass cards, rounded borders (`var(--border-radius-md)`).
- **Responsiveness**: Flexible CSS grid and flexbox containers supporting desktop, tablet, and mobile displays.
