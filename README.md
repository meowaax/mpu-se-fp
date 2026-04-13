# Qwen CRM Assistant

An AI-powered CRM dashboard built with **Flask**, **PostgreSQL**, and **Qwen API**.  
This project combines a simple sales dashboard with a chatbot assistant that can answer questions about CRM data such as deals, accounts, stages, and quarterly targets.

## Features

- Dashboard for deals, accounts, and targets
- AI chatbot powered by Qwen API
- Backend API built with Flask
- PostgreSQL integration for CRM data
- Interactive charts with Chart.js
- Environment-variable based configuration with `.env`

## Project Structure

```text
qwen-crm-assistant-complete/
├── index.html           # Main frontend page
├── style.css            # Custom styles
├── app.js               # Dashboard logic
├── chatbot.js           # Chatbot frontend logic
├── server.py            # Flask backend
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore           # Ignore sensitive/local files
├── README.md            # Project documentation
└── REFERENCES.md        # References and acknowledgements
```

## Requirements

### Software
- Python 3.10 or above
- PostgreSQL 14 or above
- Modern browser (Chrome, Edge, Firefox)

### Python Packages
See `requirements.txt`:

```txt
Flask==3.1.0
python-dotenv==1.0.1
psycopg2-binary==2.9.9
requests==2.32.3
```

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd qwen-crm-assistant-complete
```

### 2. Create and activate a virtual environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

You can copy `.env.example` and edit it:

#### Windows
```bash
copy .env.example .env
```

#### macOS / Linux
```bash
cp .env.example .env
```

Then fill in your own values:

```env
QWEN_API_KEY=your_qwen_api_key_here
QWEN_MODEL=qwen3.5-flash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
```

## Database Setup

This project expects PostgreSQL tables similar to:

- `deals_raw`
- `accounts_raw`
- `sales_targets_raw`

The backend reads CRM data from these tables and exposes them through:

- `GET /api/crm-data`
- `POST /api/chat`

If the database is unavailable, the chatbot may still work, but detailed CRM analysis will be limited.

## How to Use

### Start the backend

```bash
python server.py
```

The Flask server will start at:

```text
http://127.0.0.1:8000
```

### Open the application

Open your browser and visit:

```text
http://127.0.0.1:8000
```

### Use the dashboard

You can:

- View dashboard summary cards
- Explore deals by stage
- View accounts and targets
- Ask the AI assistant questions such as:
  - "Total sales"
  - "Deals by stage"
  - "Top accounts"
  - "Summarize quarterly target progress"

## API Endpoints

### `GET /api/crm-data`
Returns CRM data from PostgreSQL.

### `POST /api/chat`
Sends a user message plus CRM context to the Qwen API.

Example request body:

```json
{
  "message": "Summarize the pipeline",
  "history": [],
  "crmContext": {
    "deals": [],
    "accounts": [],
    "targets": []
  }
}
```

## Notes for GitHub Upload

- Do **not** upload your real `.env` file
- Keep `.env` in `.gitignore`
- Upload only `.env.example`
- If an API key was exposed before, regenerate it before publishing

## Limitations

- This project depends on external Qwen API access
- PostgreSQL sample tables must exist for full CRM analytics
- The frontend currently assumes a fixed CRM schema

## References

See `REFERENCES.md`.
