# AI-Powered CRM Assistant； Data Gap Bridge
## 1. Graphical Abstract
![Project Overview]

## 2. Project Demonstration (Demo) 
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

---

## 3. Purpose of the Software
### 3.1 Problem Statement
Traditional CRM systems are often complex and restricted to specialized users, creating operational bottlenecks. Our AI-Powered CRM Assistant enables non-technical stakeholders to access strategic information through simple conversational queries.

### 3.2 Software Development Process
**Model:** **Agile Development**
**Reasoning:** Agile allows our team to work in parallel on the chatbot logic, frontend, and database design. [cite_start]It supports iterative testing, which is crucial for refining AI prompt accuracy
**Target Market:** Small to medium enterprises (SMEs) and multi-departmental companies seeking higher data visibility
### 3.3 Target Market & Market Analysis

#### A. Target Audience
Our primary target market includes **Small to Medium Enterprises (SMEs)** and non-technical departments within larger organizations (e.g., Marketing, HR, and Executive Leadership) that lack dedicated data analysts.

#### B. Market Pain Points (The "Expert Bottleneck")
Currently, CRM data is often "locked" behind complex UI menus or requires technical expertise to query. This creates a dependency on CRM experts, leading to decision-making delays.

#### C. Our Solution's Positioning
Our AI-Powered Assistant fills the gap between **Complex Data Storage** and **Strategic Decision Making** by providing:
* **Zero Learning Curve:** No need to learn complex CRM navigation.
* **Instant Insights:** Get sales summaries or customer lists in seconds via chat.
* **Cross-Departmental Visibility:** Empowers every team member with data-driven insights.

---

## 4. Software Development Plan
### 4.1 Team Members & Responsibilities
| Member | Primary Roles | Key Responsibilities |
| :--- | :--- | :--- |
| **Lucas** | Chatbot Developer | Developing AI logic; Connecting chatbot to the DBMS. |
| **Gustavo** | Frontend Developer | Web development and UI/UX implementation. |
| **Anna** | DB Designer / Reviewer | Sourcing datasets; Database schema design; Documentation review. |
| **Eddie** | Documentation Lead | README.md drafting; Project report management. |

### 4.2 Project Schedule
* **Week 1:** Requirement analysis and database setup (DBMS commitment).
* **Week 2:** Parallel development of Chatbot logic and Web Frontend.
* **Week 2.5:** System integration and "Analysis Capabilities" testing phase.
* **Week 3:** Final demo recording and documentation polishing.

### 4.3 Algorithm & Implementation
* **Data Handling:** We utilize the **Lightdash Demo Training** dataset.
* **Prompt Logic:** To handle historical data limitations in the demo, the AI is anchored to a specific virtual date (e.g., `2021.01.01`). This ensures relative queries like "last month" yield accurate results from the 2020 dataset.

### 4.4 Current Status & Future Plan
**Current Status:** **Pilot Level**. Functional CRUD operations and AI query parsing.
**Future Plan:** Integration of live enterprise datasets and real-time system clock synchronization to replace the anchored prompt logic.

---

## 5. Development & Running Environments

---

## 6. Declaration
