# 📘 Project Overview & Architecture

## 🎯 Introduction

**EduSense** (AI Student Performance Monitoring & Master Data Management System) is an enterprise-grade academic analytics web application tailored for higher education institutions. Developed for the **Department of Artificial Intelligence and Data Science** at **Jayaraj Annapackiam C. S. I. College of Engineering**, the application automates student risk identification, faculty & departmental master data management, generative AI queries, and automated SMTP email warnings.

---

## 🔄 End-to-End System Workflow

```
┌─────────────────────────┐
│ Excel Markbook Upload   │ (Multi-sheet workbooks: I1, I2, I3, RUBRICS, IAT)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Parsing & Normalization │ (Extracted: Reg No, Name, Marks, Attendance, Assignments)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ MySQL Database Storage  │ (Persistent storage in edusense_db with SQLite fallback)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Rule-Based Risk Engine  │ (Evaluates dynamic thresholds for Attendance, Marks, Assignment)
└───────────┬─────────────┘
            │
  ┌─────────┼───────────────────────────┬───────────────────────────┐
  ▼         ▼                           ▼                           ▼
┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
│ Dashboard Analytics   │   │ Master Data Manager   │   │ Gemini AI Assistant   │   │ Bulk SMTP Alert       │
│ & Visual KPI Cards    │   │ (Staffs, Depts, Years)│   │ (Dataset RAG Prompt)  │   │ Dispatcher Engine     │
└───────────────────────┘   └───────────────────────┘   └───────────────────────┘   └───────────────────────┘
```

---

## 🔑 Key Capabilities

1. **Multi-Format Excel Markbook Import**: Ingests official multi-sheet college markbooks (`I1`, `I2`, `I3`, `RUBRICS`, `IAT-REPORT`) and flat `.xlsx` spreadsheets.
2. **Rule-Based Early Warning System**: Automatically flags students as **Good Standing**, **Warning Status**, or **At Risk** using customizable threshold parameters.
3. **Master Data & Faculty Roster Manager**: Full CRUD management interface (`/management`) for adding and removing teaching staff, academic departments, and graduation batches.
4. **Google Gemini AI Integration**: Provides dataset-grounded responses to natural language queries (*"List students with low attendance in ADS department"*) with automatic offline reasoning fallback.
5. **Automated Email Alerting**: Sends personalized warning emails to students and guardians via configurable SMTP servers.
6. **Modern Design System**: Built with Plus Jakarta Sans typography, glassmorphism, responsive grid layouts, and interactive Chart.js visualizations.
