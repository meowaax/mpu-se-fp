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

def get_all_tables():
    """Get all tables in the database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return [table['name'] for table in tables]

def get_table_schema():
    """Get schema for all tables in the database"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    schema = {}
    for table in tables:
        table_name = table['name']
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        schema[table_name] = [col['name'] for col in columns]
    
    conn.close()
    return schema

def get_sample_data(table_name, limit=2):
    """Get sample data from a table for context"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        sample = [dict(row) for row in rows]
    except Exception as e:
        sample = []
    
    conn.close()
    return sample

def execute_query(query):
    """Execute SQL query and return results"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            conn.close()
            return {"success": True, "data": results, "row_count": len(results)}
        else:
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            return {"success": True, "affected_rows": affected_rows, "data": []}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e), "data": []}

def generate_sql_query(user_message, schema, sample_data):
    """Generate SQL query using Qwen API based on user request"""
    api_key = os.getenv('QWEN_API_KEY')
    model = os.getenv('QWEN_MODEL', 'qwen-plus')
    
    if not api_key:
        return None, "API key not configured"
    
    # Virtual anchor date for consistent relative time queries
    VIRTUAL_ANCHOR_DATE = "2023-12-31"
    VIRTUAL_ANCHOR_YEAR = "2023"
    VIRTUAL_ANCHOR_MONTH = "12"
    
    system_prompt = f"""You are a SQL expert. Convert the user's natural language question into a SQL query for a SQLite database.

**IMPORTANT DATE CONTEXT:**
- The current virtual date is {VIRTUAL_ANCHOR_DATE} 
- All date-related queries should be interpreted relative to this virtual anchor date
- For "last month" queries, refer to November 2023
- For "this year" queries, refer to 2023
- For "last year" queries, refer to 2022

Database Schema:
{json.dumps(schema, indent=2)}

Sample Data from Tables:
{json.dumps(sample_data, indent=2)}


Rules:
1. Return ONLY the SQL query, no explanation or additional text
2. Use SQLite syntax
3. Use the exact table and column names from the schema above
4. Be careful with string matching - use LIKE for partial matches
5. Use COALESCE or handle NULL values appropriately
6. For aggregation queries, use appropriate GROUP BY clauses
7. Limit results to 100 rows max unless specified
8. If the question is ambiguous, make reasonable assumptions
9. Join tables when necessary using foreign keys (account_id, etc.)
10. For date comparisons, use SQLite date functions (strftime, date, etc.)
11. When users ask about "last month", "last quarter", or "last year", calculate based on {VIRTUAL_ANCHOR_DATE}

Date calculation examples (based on virtual date {VIRTUAL_ANCHOR_DATE}):
- "last month" -> strftime('%Y-%m', date_column) = '2023-11'
- "this year" -> strftime('%Y', date_column) = '{VIRTUAL_ANCHOR_YEAR}'
- "last year" -> strftime('%Y', date_column) = '2022'
- "year to date" -> dates from {VIRTUAL_ANCHOR_YEAR}-01-01 to {VIRTUAL_ANCHOR_DATE}
- "previous month" -> November 2023

Examples based on typical CRM tables:
- "Show me all deals" -> "SELECT * FROM deals LIMIT 50"
- "What's the total sales value?" -> "SELECT SUM(amount) as total_sales FROM deals"
- "List accounts with their deal count" -> "SELECT a.account_name, COUNT(d.deal_id) as deal_count FROM accounts a LEFT JOIN deals d ON a.account_id = d.account_id GROUP BY a.account_id"
- "Show me won deals" -> "SELECT * FROM deals WHERE stage LIKE '%Won%'"
- "What's the average deal amount?" -> "SELECT AVG(amount) as average_amount FROM deals"
- "Deals from last month" -> "SELECT * FROM deals WHERE strftime('%Y-%m', created_date) = '2023-11'"
- "Total sales this year" -> "SELECT SUM(amount) FROM deals WHERE strftime('%Y', created_date) = '{VIRTUAL_ANCHOR_YEAR}'"
- "Compare this year vs last year" -> "SELECT strftime('%Y', created_date) as year, SUM(amount) as total FROM deals WHERE strftime('%Y', created_date) IN ('{VIRTUAL_ANCHOR_YEAR}', '2022') GROUP BY year"

User question: {user_message}

SQL Query:"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 300
    }
    
    try:
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            sql_query = result['choices'][0]['message']['content'].strip()
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            return sql_query, None
        else:
            return None, f"API Error: {response.status_code}"
    except Exception as e:
        return None, str(e)

def format_response_as_human_language(query_result, user_message):
    """Format database results as natural language using Qwen API"""
    api_key = os.getenv('QWEN_API_KEY')
    model = os.getenv('QWEN_MODEL', 'qwen-plus')
    
    VIRTUAL_ANCHOR_DATE = "December 31, 2023"
    
    if not api_key or not query_result.get('success'):
        if not query_result.get('success'):
            return f"Error: {query_result.get('error', 'Unknown error')}"
        return format_results_simple(query_result['data'], user_message)
    
    system_prompt = """You are a helpful CRM assistant. Convert the database query results into a natural, conversational response.

*IMPORTANT CONTEXT:**
- The current virtual date is {VIRTUAL_ANCHOR_DATE}
- All dates in the response should be interpreted relative to this anchor
- When referencing time periods (like "last month"), make it clear you're referring to the period relative to {VIRTUAL_ANCHOR_DATE}

Rules:
- Be concise but informative
- Use proper formatting for numbers (commas, currency symbols)
- If there are many results, summarize or list the most relevant ones
- Never mention SQL or database terminology
- Answer directly based on the data provided"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User asked: '{user_message}'\n\nDatabase results: {json.dumps(query_result['data'][:20])}\nTotal rows: {query_result['row_count']}\n\nRespond naturally, keeping in mind the virtual date is {VIRTUAL_ANCHOR_DATE}:"}
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return format_results_simple(query_result['data'], user_message)
    except Exception as e:
        return format_results_simple(query_result['data'], user_message)

def format_results_simple(data, user_message):
    """Simple fallback formatter for database results"""
    if not data:
        return "No results found for your query."
    
    if len(data) == 1 and len(data[0]) == 1:
        value = list(data[0].values())[0]
        if value is None:
            return "No data found."
        return f"The result is: {value:,}" if isinstance(value, (int, float)) else f"The result is: {value}"
    
    if len(data) <= 5:
        result_text = f"Found {len(data)} item(s):\n"
        for item in data:
            result_text += f"• {', '.join([f'{k}: {v}' for k, v in item.items()])}\n"
        return result_text
    else:
        return f"Found {len(data)} results. Showing first 5:\n" + "\n".join([
            f"• {', '.join([f'{k}: {v}' for k, v in item.items()])}" 
            for item in data[:5]
        ])

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/crm-data')
def get_crm_data():
    """Fetches CRM data from normal tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Deals from normal deals table
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
        
        # Accounts from normal accounts table
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
        
        # Targets from normal sales_target table
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
        
        # Fallback sample data
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
    """Chatbot with direct database access using normal tables"""
    try:
        data = request.json
        user_message = data.get('message', '')
        history = data.get('history', [])
        
        print(f"📝 User message: {user_message}")
        
        # Check if database exists
        if not os.path.exists(DATABASE_PATH):
            return jsonify({'reply': 'Database not found. Please ensure the database is properly set up.'}), 500
        
        # Get all tables schema
        schema = get_table_schema()
        all_tables = get_all_tables()
        
        if not schema:
            return jsonify({'reply': 'No tables found in the database.'}), 500
        
        print(f"📊 Tables found: {list(schema.keys())}")
        
        # Get sample data for context
        sample_data = {}
        for table_name in schema.keys():
            sample_data[table_name] = get_sample_data(table_name, 2)
        
        # Generate SQL query using AI
        sql_query, error = generate_sql_query(user_message, schema, sample_data)
        
        if error:
            print(f"❌ Query generation error: {error}")
            # Fallback to simple keyword-based responses
            '''
            fallback_response = handle_fallback_response(user_message)
            if fallback_response:
                return jsonify({'reply': fallback_response})'''
            return jsonify({'reply': f"I couldn't understand your request. Could you please rephrase it?"}), 200
        
        print(f"🔍 Generated SQL: {sql_query}")
        
        # Validate query is a SELECT statement for safety
        if not sql_query.strip().upper().startswith('SELECT'):
            return jsonify({'reply': "I can only answer questions about your data (SELECT queries only)."}), 200
        
        # Execute the query
        query_result = execute_query(sql_query)
        
        if not query_result['success']:
            print(f"❌ Query execution error: {query_result['error']}")
            return jsonify({'reply': f"Sorry, I encountered an error: {query_result['error']}"}), 200
        
        print(f"✅ Query executed successfully. Found {query_result['row_count']} rows")
        
        # Format the response
        if query_result['row_count'] == 0:
            response_text = "No results found for your query."
        else:
            response_text = format_response_as_human_language(query_result, user_message)
        
        return jsonify({'reply': response_text})
        
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
        # Account data from normal tables
        cursor.execute("SELECT * FROM accounts WHERE account_id = ?", [account_id])
        account = dict(cursor.fetchone())
        
        # Account users
        cursor.execute("SELECT * FROM users WHERE account_id = ?", [account_id])
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

@app.route('/api/db/status', methods=['GET'])
def db_status():
    """Check database status and show all tables"""
    try:
        all_tables = get_all_tables()
        schema = get_table_schema()
        
        # Get row counts for each table
        conn = get_db()
        cursor = conn.cursor()
        row_counts = {}
        for table in all_tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            result = cursor.fetchone()
            row_counts[table] = result['count']
        conn.close()
        
        return jsonify({
            'database_exists': os.path.exists(DATABASE_PATH),
            'database_path': DATABASE_PATH,
            'tables': all_tables,
            'total_tables': len(all_tables),
            'row_counts': row_counts,
            'schema': schema
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/chat/history', methods=['POST'])
def clear_chat_history():
    """Endpoint to clear chat history (optional)"""
    return jsonify({'status': 'success', 'message': 'Chat history cleared'})

@app.route('/api/test-qwen', methods=['GET'])
def test_qwen():
    """Test if Qwen API is working"""
    api_key = os.getenv('QWEN_API_KEY')
    
    if not api_key:
        return jsonify({'error': 'QWEN_API_KEY not set in environment variables'}), 500
    
    # Test simple API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen-plus",
        "messages": [{"role": "user", "content": "Say 'API is working'"}],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'status': 'success',
                'response': result['choices'][0]['message']['content'],
                'api_key_configured': True
            })
        else:
            return jsonify({
                'status': 'error',
                'status_code': response.status_code,
                'response_text': response.text,
                'api_key_configured': True
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'api_key_configured': True
        }), 500

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DATABASE_PATH):
        print(f"⚠️ Database not found at: {DATABASE_PATH}")
        print("Please ensure the database exists at db/crm.db")
    else:
        print(f"✅ Database found: {DATABASE_PATH}")
        # Show available tables
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        if tables:
            print(f"✅ Found tables: {[t['name'] for t in tables]}")
        else:
            print(f"⚠️ No tables found in the database.")
        conn.close()
    
    app.run(host='127.0.0.1', port=8000, debug=True)