# Qwen CRM Assistant: Bridging the Data Gap

## 1. Graphical Abstract
<img width="1920" height="1080" alt="38494f925984eb9773c29858c9cbf39f" src="https://github.com/user-attachments/assets/5de6f1f9-acf9-445d-90ff-6f4c1e5dac27" />


An AI-powered CRM dashboard built with **Flask**, **SQLite**, and **Qwen API**.  
This project combines a comprehensive sales dashboard with an intelligent chatbot assistant that can answer questions about CRM data such as deals, accounts, pipeline stages, and quarterly targets.

## ✨ Features

- 📊 **Interactive Dashboard** – View total pipeline value, closed won deals, active deals, and performance charts
- 🤖 **AI Chatbot Assistant** – Powered by Qwen API for natural language queries about your CRM data
- 🗄️ **SQLite Database** – Lightweight, file-based database with full CRM schema (no PostgreSQL required)
- 📈 **Data Visualization** – Dynamic charts built with Chart.js
- 🔧 **Automated Setup** – One-click `.bat` installer for Windows (installs all dependencies automatically)
- 🐍 **Flask Backend** – RESTful API with proper error handling and fallbacks
- 🔒 **Environment Configuration** – Secure API key management via `.env` file
---

## 2. Project Demonstration (Demo)

Video available on Youtube: [Click here](https://youtu.be/jnf9_QIUuQo)

---

## 3. Purpose of the Software
### 3.1 Problem Statement
Traditional CRM systems are often complex and restricted to specialized users, creating operational bottlenecks. Our AI-Powered CRM Assistant enables non-technical stakeholders to access strategic information through simple conversational queries.

### 3.2 Software Development Process
* **Model:** **Agile Development**.
* **Reasoning:** Agile allows our team to work in parallel on the chatbot logic, frontend, and database design.It supports iterative testing, which is crucial for refining AI prompt accuracy.
* **Target Market:** Small to medium enterprises (SMEs) and multi-departmental companies seeking higher data visibility.

---

## 4. Software Development Plan
### 4.1 Team Members & Responsibilities (R&R)

| Member | Primary Roles | Key Responsibilities |
| :--- | :--- | :--- |
| **Lucas** | Chatbot Developer | Developing AI logic; Connecting chatbot to the DBMS. |
| **Gustavo** | Frontend Developer | Web development and UI/UX implementation. |
| **Anna** | DB Designer / Reviewer | Sourcing datasets; Database schema design; Documentation review. |
| **Eddie** | Documentation Lead | README.md drafting; Project report management. |

### 4.2 Project Schedule
**Week 1:** Requirement analysis and database setup (DBMS commitment).
* **Week 1-2:** Parallel development of Chatbot logic and Web Frontend.
* **Week 3-4:** System integration and "Analysis Capabilities" testing phase.
* **Week 4:** Final demo recording and documentation polishing.

### 4.3 Algorithm & Implementation
* **Data Handling:** We utilize the **Lightdash Demo Training** dataset.
* **Prompt Logic:** To handle historical data limitations in the demo, the AI is anchored to a specific virtual date (e.g., `2023.12.31`). This ensures relative queries like "last month" yield accurate results from the 2020 dataset.

### 4.4 Current Status & Future Plan
* **Current Status:** **Pilot Level**. Functional CRUD operations and AI query parsing.
* **Future Plan:** Integration of live enterprise datasets and real-time system clock synchronization to replace the anchored prompt logic.

---

## 5. Development & Running Environments
## 📁 Project Structure

```text
qwen-crm-assistant-complete/
├── index.html              # Main frontend dashboard
├── style.css               # Custom styles and animations
├── app.js                  # Dashboard logic and data management
├── chatbot.js              # Chatbot frontend interface
├── server.py               # Flask backend API
├── setup.bat               # 🚀 One-click Windows installer
├── .env.example            # Example environment configuration
├── .gitignore              # Ignore sensitive/local files
├── README.md               # Project documentation
├── REFERENCES.md           # References documentation
├── db/
│   ├── crm.db              # SQLite database
│   ├── database.py         # Database migration script
│   └── seeds/              # CSV seed files (optional)
│   └── diagram.png     
```

## 🔧 Requirements

### Software

- Python 3.10 or higher
- Modern web browser (Chrome, Edge, Firefox)
- Windows (for .bat installer) or any OS with Python

### Python Packages (Auto-installed)

The setup script installs these automatically:

- `Flask==3.1.0` – Web framework
- `python-dotenv==1.0.1` – Environment variable management
- `requests==2.32.3` – HTTP client for Qwen API
- `pandas==2.2.3` – Data manipulation and CSV import
- `black==24.3.0` – Code formatter (development)

## 🚀 Quick Start (Windows)

### Option 1: One-Click Installer (Recommended)

1. Download or clone this repository
2. Double-click `setup.bat`
3. The script will automatically:

   - ✅ Check Python installation
   - ✅ Create a virtual environment
   - ✅ Install all required packages
   - ✅ Verify database setup
   - ✅ Create `.env` file (if missing)
   - ✅ Start the Flask server
   - ✅ Open your browser to `http://127.0.0.1:8000`

### Option 2: Manual Installation

```bash
# Clone the repository
git clone <your-repository-url>
cd qwen-crm-assistant-complete

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install Flask==3.1.0 python-dotenv==1.0.1 requests==2.32.3 pandas==2.2.3

# Configure environment
copy .env.example .env   # Windows
cp .env.example .env     # macOS / Linux

# Edit .env and add your Qwen API key
# QWEN_API_KEY=sk-your-actual-api-key-here
# QWEN_MODEL=qwen-plus

# Start the server
python server.py
```

## 🔑 Environment Configuration

Create a `.env` file in the project root with:

```env
# Qwen API Configuration (REQUIRED)
QWEN_API_KEY=sk-your-qwen-api-key-here
QWEN_MODEL=qwen-plus

# Database Configuration (OPTIONAL - defaults to SQLite)
# DATABASE_URL=sqlite:///db/crm.db
```

Get your Qwen API key from: [Aliyun DashScope Console](https://dashscope.console.aliyun.com/)

## 📊 Database Schema

The project uses a normalized SQLite database with the following tables:

| Table        | Description                          | Records (Sample) |
|--------------|--------------------------------------|------------------|
| accounts     | Customer/company information         | 1,005            |
| users        | System users                         | 6,006            |
| deals        | Sales opportunities/deals            | 1,084            |
| sales_target | Quarterly sales targets              | 64               |
| user_deals   | Many-to-many user-deal assignments   | 3,408            |
| tracks       | User activity tracking               | 100,007          |
| addresses    | User addresses                       | 6,080            |
| countries    | Country reference data               | 8                |

**Total Pipeline Value:** ~$8.7M across 1,084 active deals

## 💾 Data Import

To import data from CSV files:

```bash
cd db
python database.py
```

## 💡 Usage Guide

### Dashboard Navigation

- **Dashboard** – Overview of pipeline, deals by stage, and targets
- **Deals** – View and manage all sales opportunities
- **Accounts** – Browse customer accounts and their deal history
- **Targets** – Track progress against quarterly sales goals

### AI Assistant Commands

Ask the chatbot natural language questions like:

- "What's the total sales value?"
- "Show me deals by stage"
- "Who are our top 5 accounts?"
- "How are we tracking against Q2 targets?"
- "List all deals over $100,000"
- "Summarize the current pipeline"

**Quick Questions:** Click the quick-action buttons below the chat input for instant answers.

## 🔌 API Endpoints

**GET /api/crm-data**  
Returns complete CRM dataset including deals, accounts, and targets.

**Response:**
```json
{
  "deals": [...],
  "accounts": [...],
  "targets": [...]
}
```

**POST /api/chat**  
Sends user message and CRM context to Qwen API for intelligent responses.

**Request:**
```json
{
  "message": "What's our total pipeline value?",
  "history": [...],
  "crmContext": {
    "deals": [...],
    "accounts": [...],
    "targets": [...]
  }
}
```

**Response:**
```json
{
  "reply": "Based on current CRM data, the total pipeline value is $8,688,875 across 1,084 active deals."
}
```

**GET /api/accounts/<account_id>**  
Returns detailed information for a specific account.

**GET /api/check-database**  
Debug endpoint to verify database connectivity and record counts.

## 🛠️ Development Tools

### Format Code with Black

```bash
# Format all Python files
black server.py db/*.py
```

### Database Browser

We recommend [DB Browser for SQLite](https://sqlitebrowser.org/) for visual database exploration.



---

## 6. Declaration
* **Open Source:** We utilize the `lightdash-demo-training` dataset.
* **AI API:** Natural language parsing is assisted by [Specify API, e.g., OpenAI API].
*All other core integration and CRM logic were developed by the team.

## 🚧 Limitation

- Qwen API requires an active internet connection and valid API key
- The free tier of Qwen API has rate limits (check your quota)
- Frontend assumes the standard CRM schema; custom fields require code updates
- Large datasets (>100,000 records) may impact dashboard performance

## 🔜 Future Enhancements

- User authentication and multi-tenancy
- Real-time data updates via WebSockets
- Advanced filtering and search
- Export reports to PDF/Excel
- Docker containerization
- Cloud deployment templates (Render, Railway, AWS)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open-source and available under the MIT License.

## 🙏 Acknowledgments

- Qwen API by Alibaba Cloud – Powering the AI assistant
- Chart.js – Beautiful, responsive charts
- Tailwind CSS – Utility-first CSS framework
- Font Awesome – Icon library
