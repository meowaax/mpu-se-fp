import json
import os
from pathlib import Path

import psycopg2
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from psycopg2.extras import RealDictCursor


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")

QWEN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
DEFAULT_MODEL = os.getenv("QWEN_MODEL", "qwen3.5-flash")
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"


def get_database_url():
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_db_connection():
    conn = psycopg2.connect(get_database_url())
    conn.autocommit = True
    return conn


def format_quarter_label(value):
    quarter = ((value.month - 1) // 3) + 1
    return f"{value.year} Q{quarter}"


def build_prompt_context(crm_context):
    deals = crm_context.get("deals", [])
    accounts = crm_context.get("accounts", [])
    targets = crm_context.get("targets", [])

    total_pipeline = sum((deal.get("amount") or 0) for deal in deals)
    won_deals = [deal for deal in deals if deal.get("stage") in {"Won", "Closed Won"}]
    active_deals = [
        deal
        for deal in deals
        if deal.get("stage") not in {"Won", "Closed Won", "Lost", "Closed Lost"}
    ]

    stage_breakdown = {}
    industry_breakdown = {}
    for deal in deals:
        stage = deal.get("stage") or "Unknown"
        industry = deal.get("industry") or "Unknown"
        amount = deal.get("amount") or 0

        stage_entry = stage_breakdown.setdefault(stage, {"stage": stage, "count": 0, "amount": 0})
        stage_entry["count"] += 1
        stage_entry["amount"] += amount

        industry_entry = industry_breakdown.setdefault(
            industry,
            {"industry": industry, "count": 0, "amount": 0, "avg_amount": 0},
        )
        industry_entry["count"] += 1
        industry_entry["amount"] += amount

    industry_rows = []
    for row in industry_breakdown.values():
        row["avg_amount"] = round(row["amount"] / row["count"], 2) if row["count"] else 0
        industry_rows.append(row)

    return {
        "snapshot": {
            "deal_count": len(deals),
            "account_count": len(accounts),
            "total_pipeline_value": total_pipeline,
            "won_deal_count": len(won_deals),
            "won_deal_value": sum((deal.get("amount") or 0) for deal in won_deals),
            "active_deal_count": len(active_deals),
        },
        "stage_breakdown": sorted(stage_breakdown.values(), key=lambda item: item["amount"], reverse=True),
        "industry_breakdown": sorted(industry_rows, key=lambda item: item["amount"], reverse=True),
        "top_accounts": sorted(
            [
                {
                    "name": account.get("name"),
                    "industry": account.get("industry"),
                    "segment": account.get("segment"),
                    "deals": account.get("deals"),
                    "total_value": account.get("totalValue"),
                }
                for account in accounts
            ],
            key=lambda item: item["total_value"] or 0,
            reverse=True,
        )[:12],
        "recent_deals": [
            {
                "account": deal.get("account"),
                "industry": deal.get("industry"),
                "plan": deal.get("plan"),
                "amount": deal.get("amount"),
                "stage": deal.get("stage"),
                "date": deal.get("date"),
            }
            for deal in deals[:20]
        ],
        "targets": targets,
    }


def fetch_crm_context():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    d.deal_id::text AS id,
                    COALESCE(a.account_name, 'Unknown Account') AS account,
                    COALESCE(a.industry, 'Unknown') AS industry,
                    COALESCE(a.segment, 'Unknown') AS segment,
                    COALESCE(d.plan, 'Unknown') AS plan,
                    COALESCE(d.seats, 0) AS seats,
                    COALESCE(d.amount, 0) AS amount,
                    COALESCE(d.stage, 'Unknown') AS stage,
                    d.created_date::date AS date,
                    'Demo User' AS owner
                FROM deals_raw d
                LEFT JOIN accounts_raw a ON d.account_id = a.account_id
                ORDER BY d.created_date DESC, d.deal_id
                """
            )
            deals = cur.fetchall()
            for deal in deals:
                if deal["date"] is not None:
                    deal["date"] = deal["date"].strftime("%Y-%m-%d")

            cur.execute(
                """
                SELECT
                    a.account_id::text AS id,
                    a.account_name AS name,
                    a.segment,
                    a.industry,
                    COUNT(d.deal_id)::int AS deals,
                    COALESCE(SUM(d.amount), 0)::int AS "totalValue"
                FROM accounts_raw a
                LEFT JOIN deals_raw d ON d.account_id = a.account_id
                GROUP BY a.account_id, a.account_name, a.segment, a.industry
                ORDER BY COALESCE(SUM(d.amount), 0) DESC, a.account_name ASC
                """
            )
            accounts = cur.fetchall()

            cur.execute(
                """
                WITH quarterly_targets AS (
                    SELECT
                        quarter_start_date::date AS quarter_start,
                        COALESCE(SUM(target_amount), 0)::int AS target_amount
                    FROM sales_targets_raw
                    GROUP BY quarter_start_date::date
                ),
                quarterly_achieved AS (
                    SELECT
                        date_trunc('quarter', created_date)::date AS quarter_start,
                        COALESCE(SUM(amount), 0)::int AS achieved_amount
                    FROM deals_raw
                    WHERE stage IN ('Won', 'Closed Won')
                    GROUP BY date_trunc('quarter', created_date)::date
                )
                SELECT
                    qt.quarter_start,
                    qt.target_amount AS target,
                    COALESCE(qa.achieved_amount, 0) AS achieved
                FROM quarterly_targets qt
                LEFT JOIN quarterly_achieved qa ON qa.quarter_start = qt.quarter_start
                ORDER BY qt.quarter_start
                """
            )
            targets = cur.fetchall()
            for target in targets:
                target["month"] = format_quarter_label(target.pop("quarter_start"))

        return {
            "deals": deals,
            "accounts": accounts,
            "targets": targets,
        }
    finally:
        conn.close()


def build_system_prompt(crm_context):
    prompt_context = build_prompt_context(crm_context)

    return (
        "You are a CRM copilot for a sales dashboard. "
        "Answer in concise English unless the user writes in Chinese, then answer in Chinese. "
        "Use the CRM summary below when relevant, and do not invent numbers that are not present. "
        "If the user asks for analysis, summarize key figures clearly and mention assumptions. "
        "If a question needs detail beyond this summary, say that a deeper database query is needed.\n\n"
        f"CRM summary: {json.dumps(prompt_context, ensure_ascii=False)}"
    )


def extract_reply(data):
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("Unexpected Qwen response format.") from exc

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        reply = "\n".join(part for part in text_parts if part).strip()
        if reply:
            return reply

    raise ValueError("Qwen did not return text content.")


@app.route("/")
def serve_index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(BASE_DIR, filename)


@app.get("/api/crm-data")
def get_crm_data():
    try:
        return jsonify(fetch_crm_context())
    except psycopg2.Error as exc:
        return jsonify(
            {
                "error": (
                    "Unable to load CRM data from PostgreSQL. "
                    f"Check DATABASE_URL and confirm the Lightdash demo tables are available. Details: {exc}"
                )
            }
        ), 503


@app.post("/api/chat")
def chat():
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        return jsonify({"error": "QWEN_API_KEY is not configured in .env."}), 500

    payload = request.get_json(silent=True) or {}
    user_message = (payload.get("message") or "").strip()
    history = payload.get("history") or []
    crm_context = payload.get("crmContext") or {}

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    try:
        crm_context = fetch_crm_context()
    except psycopg2.Error:
        pass

    messages = [{"role": "system", "content": build_system_prompt(crm_context)}]
    for item in history[-8:]:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content.strip()})

    messages.append({"role": "user", "content": user_message})

    try:
        response = requests.post(
            QWEN_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEFAULT_MODEL,
                "messages": messages,
                "temperature": 0.7,
            },
            timeout=45,
        )
    except requests.RequestException as exc:
        return jsonify({"error": f"Unable to connect to Qwen API: {exc}"}), 502

    if not response.ok:
        detail = response.text
        try:
            detail = response.json()
        except ValueError:
            pass
        return jsonify({"error": f"Qwen API error: {detail}"}), response.status_code

    try:
        reply = extract_reply(response.json())
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
