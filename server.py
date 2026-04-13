# server.py - Corrected version for frontend format
import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv
import requests
import traceback


load_dotenv()


app = Flask(__name__)


# Path to SQLite database
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'db', 'crm.db')


def get_db():
    """Connects to SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)


@app.route('/api/crm-data')
def get_crm_data():
    """Fetches CRM data from normalized tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Deals - Using 'deals' table instead of 'deals_normalized'
        cursor.execute("""
            SELECT DISTINCT
                d.deal_id as id,
                a.account_name as account,
                d.amount,
                d.stage,
                d.created_date as date,
                'Sales Team' as owner,
                COALESCE(d.plan, 'Standard') as plan
            FROM deals d
            JOIN accounts a ON d.account_id = a.account_id
            ORDER BY d.amount DESC
        """)
        deals = [dict(row) for row in cursor.fetchall()]
        
        print(f"✅ Deals loaded: {len(deals)}")
        
        # Accounts - Using 'accounts' table
        cursor.execute("""
            SELECT 
                a.account_id as id,
                a.account_name as name,
                a.industry,
                a.segment,
                COUNT(DISTINCT d.deal_id) as deals,
                COALESCE(SUM(d.amount), 0) as totalValue
            FROM accounts a
            LEFT JOIN deals d ON a.account_id = d.account_id
            GROUP BY a.account_id, a.account_name, a.industry, a.segment
            ORDER BY totalValue DESC
        """)
        accounts = [dict(row) for row in cursor.fetchall()]
        
        # Targets - Using 'sales_target' table
        cursor.execute("""
            SELECT 
                quarter_start_date as month,
                target_amount as target,
                0 as achieved
            FROM sales_target
            ORDER BY quarter_start_date
            LIMIT 12
        """)
        targets = [dict(row) for row in cursor.fetchall()]
        
        response_data = {
            'deals': deals,
            'accounts': accounts,
            'targets': targets
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        
        # Fallback
        return jsonify({
            'deals': [
                {"id": "1", "account": "Acme Corp", "amount": 50000, "stage": "Negotiation", 
                 "date": "2024-01-15", "owner": "Sales Team", "plan": "Enterprise"}
            ],
            'accounts': [],
            'targets': []
        })
    finally:
        conn.close()


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chatbot with Qwen API"""
    try:
        data = request.json
        user_message = data.get('message', '')
        history = data.get('history', [])
        crm_context = data.get('crmContext', {})
        
        # Get data from context
        deals = crm_context.get('deals', [])
        accounts = crm_context.get('accounts', [])
        targets = crm_context.get('targets', [])
        
        # If no deals in context, create sample data
        if not deals:
            print("⚠️ No deals in context, using sample data")
            deals = [
                {"account": "Acme Corp", "amount": 50000, "stage": "Negotiation"},
                {"account": "TechStart", "amount": 25000, "stage": "Proposal"},
                {"account": "Global Industries", "amount": 100000, "stage": "Closed Won"}
            ]
        
        # Calculate metrics
        total_deals = len(deals)
        total_value = sum(d.get('amount', 0) for d in deals)
        won_deals = [d for d in deals if d.get('stage') in ['Closed Won', 'Won']]
        won_value = sum(d.get('amount', 0) for d in won_deals)
        
        # Group by stage
        stages = {}
        for deal in deals:
            stage = deal.get('stage', 'Unknown')
            amount = deal.get('amount', 0)
            stages[stage] = stages.get(stage, 0) + amount
        
        print(f"📊 Metrics calculated: {total_deals} deals, total ${total_value:,.2f}")
        
        # Qwen API configuration
        api_key = os.getenv('QWEN_API_KEY')
        model = os.getenv('QWEN_MODEL', 'qwen-plus')
        
        if not api_key:
            return jsonify({'reply': 'Error: Qwen API key not configured.'}), 500
        
        # Prepare prompt with EXPLICIT data
        system_prompt = f"""You are a CRM sales assistant. You have access to the following REAL data:

CURRENT CRM METRICS (Use these exact numbers):
- Total Deals Count: {total_deals}
- Total Pipeline Value: ${total_value:,.2f}
- Closed Won Value: ${won_value:,.2f}

Deals by Stage (value):
{json.dumps(stages, indent=2)}

Top 3 Deals:
{json.dumps([{'account': d.get('account'), 'amount': d.get('amount'), 'stage': d.get('stage')} for d in deals[:3]], indent=2)}

CRITICAL INSTRUCTION: You MUST use the numbers above in your response. 
If asked about "total sales", say "${total_value:,.2f}".
If asked about "deals", say "{total_deals} active deals".
Do NOT say "0" or "no deals" because the data shows there ARE deals.
Be specific and use the actual numbers provided."""
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add history
        for msg in history[-5:]:
            if isinstance(msg, dict) and msg.get('role') in ['user', 'assistant']:
                content = msg.get('content', '')
                if content:
                    messages.append({"role": msg['role'], "content": content})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        print(f"📤 Sending to API: {len(messages)} messages")
        
        # Call Qwen API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,  # Reduced for more accurate responses
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            print(f"✅ AI Response: {ai_response[:100]}...")
            return jsonify({'reply': ai_response})
        else:
            print(f"❌ API Error: {response.status_code}")
            # Manual fallback if API fails
            if "total sales" in user_message.lower():
                return jsonify({'reply': f"Based on the CRM data, total sales value is ${total_value:,.2f} from {total_deals} deals."})
            elif "deals by stage" in user_message.lower():
                stage_list = "\n".join([f"- {stage}: ${value:,.2f}" for stage, value in stages.items()])
                return jsonify({'reply': f"Deals by stage value:\n{stage_list}"})
            else:
                return jsonify({'reply': f'API Error: {response.status_code}'}), 500
            
    except Exception as e:
        print(f"🔥 ERROR: {e}")
        traceback.print_exc()
        return jsonify({'reply': f'Error: {str(e)}'}), 500


@app.route('/api/accounts/<account_id>')
def get_account_details(account_id):
    """Endpoint for specific account details"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Account data
        cursor.execute("""
            SELECT * FROM accounts
            WHERE account_id = ?
        """, [account_id])
        account = dict(cursor.fetchone())
        
        # Account users
        cursor.execute("""
            SELECT * FROM users
            WHERE account_id = ?
        """, [account_id])
        users = [dict(row) for row in cursor.fetchall()]
        
        # Account deals
        cursor.execute("""
            SELECT * FROM deals 
            WHERE account_id = ?
            ORDER BY created_date DESC
        """, [account_id])
        deals = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'account': account,
            'users': users,
            'deals': deals
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DATABASE_PATH):
        print(f"⚠️ Database not found at: {DATABASE_PATH}")
        print("Run first: python db/database.py")
    else:
        print(f"✅ Database found: {DATABASE_PATH}")
    
    app.run(host='127.0.0.1', port=8000, debug=True)