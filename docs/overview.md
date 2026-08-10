# 📘 Project Overview & System Architecture

## 🎯 Introduction

**EduSense** (AI Student Performance Monitoring & Early Alert System) is a production-grade web application tailored for higher education institutions. Built for the **Department of Artificial Intelligence and Data Science** at **Jayaraj Annapackiam C. S. I. College of Engineering**, the system automates student performance evaluation, risk identification, AI-driven queries, and email alerts.

---

## 🔄 End-to-End Workflow

```
┌─────────────────────────┐
│ Excel Markbook Upload   │ (Multi-sheet workbooks: I1, I2, I3, RUBRICS)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Parsing & Normalization │ (Extracted: Reg No, Name, Marks, Assignment)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ MySQL Database Storage  │ (Automatic SQLite Fallback for Resilience)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Rule-Based Risk Engine  │ (Evaluates Attendance <75% and Marks <50)
└───────────┬─────────────┘
            │
  ┌─────────┴────────────────────────┐
  ▼                                  ▼
┌─────────────────────────┐        ┌─────────────────────────┐
│ Interactive Dashboard   │        │ Gemini AI Assistant     │
│ & Analytics Views       │        │ & Bulk SMTP Alerts      │
└─────────────────────────┘        └─────────────────────────┘
```

---

## 🔑 Key Capabilities

1. **Multi-Format Excel Import**: Seamlessly ingests multi-sheet college markbooks (`I1`, `I2`, `I3`, `RUBRICS`) as well as flat `.xlsx` spreadsheets.
2. **Rule-Based Risk Classification**: Automatically tags students as **Good**, **Warning**, or **At Risk** based on dynamic, configurable thresholds.
3. **Google Gemini AI Assistant**: Provides natural language query responses backed by real-time dataset context. Includes offline rule engine fallback.
4. **SMTP Email Notifications**: Dispatches individualized academic warning alerts to students flagged for poor attendance or marks.
5. **Apple-Inspired UI**: Clean, glassmorphic interface powered by modern CSS, Chart.js, and Lucide icons.
