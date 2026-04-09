## 📊 Data Source & Database Management System Justification

### 1. Lightdash Dataset Selection

The **Lightdash Demonstration Training Dataset** was selected as the foundational data source for this CRM prototype based on the following criteria:

| Criterion | Justification |
|-----------|----------------|
| **Realistic CRM Structure** | The dataset mirrors real-world CRM data models with authentic relationships between accounts, users, deals, and activity tracks. This allows the AI chatbot to answer meaningful business questions. |
| **Data Volume** | With approximately 1,000 accounts, 6,000 users, 1,000 deals, and 100,000 activity tracks, the dataset provides sufficient complexity to demonstrate the software development process without overwhelming processing requirements. |
| **Referential Integrity** | The data maintains proper foreign key relationships (`account_id` links users to accounts, `user_id` links tracks to users), enabling realistic JOIN queries that test the chatbot's SQL generation capabilities. |
| **Temporal Realism** | Includes realistic timestamps (`created_at`, `event_timestamp`) spanning multiple months, allowing time-based queries like "Show activity from last 30 days." |
| **Industry Relevance** | Contains diverse industry sectors (Financial Services, Technology, Healthcare, etc.) and customer segments (SMB, Midmarket, Enterprise), representative of actual CRM environments. |
| **Open Source Licensing** | Freely available under permissive licensing, appropriate for academic use without copyright concerns. |

**Alternative Considered:** Custom-generated data using Python Faker library was considered but rejected due to:
- Additional development time required for relationship maintenance
- Risk of unrealistic data patterns affecting demo quality
- Lack of real-world testing from an established source

**Dataset Source:** [Lightdash Demo Training Repository](https://github.com/lightdash/lightdash-demo-training)

---

### 2. SQLite Database Management System Selection

**SQLite** was selected as the database management system for this CRM prototype based on the following technical and pedagogical justifications:

#### Technical Justifications

| Criterion | Justification |
|-----------|----------------|
| **Zero Configuration** | SQLite requires no server setup, installation, or configuration. The entire database exists as a single portable file (`db/crm.db`), eliminating environment inconsistencies across development machines. |
| **Lightweight Footprint** | The complete database engine is under 20MB and runs entirely in-process with the application, making it ideal for a prototype demonstrating core CRM functionality. |
| **ACID Compliance** | SQLite fully supports ACID (Atomicity, Consistency, Isolation, Durability) transactions, ensuring data integrity during concurrent operations. |
| **Standard SQL Support** | Implements most of the SQL-92 standard, including complex JOINs, subqueries, indexes, and CHECK constraints used extensively in this project. |
| **Built-in Python Integration** | Python's `sqlite3` module is included in the standard library, eliminating external dependencies and simplifying deployment for evaluation. |
| **Cross-Platform Compatibility** | The same database file works identically on Windows, macOS, and Linux, ensuring consistent behavior across the development team's environments. |
| **Scalability for Prototype** | SQLite reliably handles databases up to 281 terabytes and can manage millions of rows, far exceeding our ~107,000 record requirement. |

#### Project-Specific Justifications

| Requirement | How SQLite Satisfies |
|-------------|---------------------|
| Rapid Prototyping | Schema changes are simple file operations without server restarts |
| Version Control Friendly | The single-file database can be committed to GitHub alongside source code |
| Demo Portability | The evaluator can run the project without installing database software |
| Focus on Core Logic | Development time focuses on chatbot AI rather than database administration |

#### Alternative DBMS Considered

| Alternative | Reason for Rejection |
|-------------|----------------------|
| **PostgreSQL** | Requires server installation, authentication setup, and network configuration — excessive complexity for a prototype. |
| **MySQL/MariaDB** | Similar server-based overhead; introduces licensing considerations. |
| **MongoDB (NoSQL)** | Document model would complicate relational queries essential for CRM (e.g., joining accounts with deals). |
| **CSV/JSON Files** | Lacks query optimization, transaction support, and referential integrity enforcement. |

#### Production Migration Path

While SQLite is optimal for this prototype, a production deployment would migrate to PostgreSQL for:
- Concurrent write access from multiple application servers
- Advanced role-based access control
- Replication and high availability requirements
- Stored procedures for complex business logic

The current SQLite implementation uses standard SQL syntax compatible with PostgreSQL, ensuring a clear migration path.

---

### 3. Combined Architecture Overview

The pairing of **Lightdash dataset** with **SQLite** enables the project to demonstrate:

| Demonstration Area | Implementation |
|--------------------|----------------|
| **Realistic Business Intelligence** | Authentic CRM data with accounts, users, deals, and activity tracking |
| **Complete Software Development Process** | Requirements → Design → Implementation → Testing lifecycle |
| **Functional AI Chatbot** | Natural language processing with intent classification and SQL generation |

---

### 4. References

- Lightdash. (n.d.). *Lightdash Demo Training Dataset*. GitHub. https://github.com/lightdash/lightdash-demo-training
- SQLite Consortium. (2024). *SQLite Documentation*. https://www.sqlite.org/docs.html
- Python Software Foundation. (2024). *sqlite3 — DB-API 2.0 interface for SQLite databases*. https://docs.python.org/3/library/sqlite3.html

Here's a simple README in English explaining what each file contains:

---

# CRM Assistant - Demo Files

## File Structure

### `index.html`
Main HTML structure of the page. Contains the sidebar, main content area, and chat interface. Links to all CSS and JavaScript files.

### `style.css`
Custom styles for animations and UI elements. Includes:
- Message slide-in animations
- Typing indicator dots
- Scrollbar hiding utilities

### `app.js`
CRM logic and functionality. Contains:
- Mock data (deals, accounts, targets)
- Dashboard rendering
- Charts (using Chart.js)
- CRUD operations for deals
- Section navigation (Dashboard, Deals, Accounts, Targets)

### `chatbot.js`
Chatbot simulation logic. Contains:
- Message display functions
- Mock AI responses (based on keywords)
- Quick question buttons
- Typing indicator animation

**Note:** This file is meant to be replaced with real chatbot API integration.

---

## Quick Start

1. Place all files in the same folder
2. Open `index.html` in a browser
3. Everything works with sample data

---

## For Developers

- To replace the chatbot: Edit `chatbot.js`
- To connect a database: Modify the `DataService` object in `app.js`
- To change styling: Edit `style.css`

---
