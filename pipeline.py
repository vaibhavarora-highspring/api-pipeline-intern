import requests
import csv
import logging
import sqlite3
from datetime import datetime

# =========================
# CONFIGURATION
# =========================
API_URL = "https://jsonplaceholder.typicode.com/users"
DB_NAME = "users.db"
CLEAN_CSV = "users_clean.csv"
LOG_FILE = "pipeline.log"

# =========================
# LOGGING SETUP
# =========================
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================
# GEO HELPERS
# =========================
def infer_continent(lat, lng):
    if lat < -60:
        return "Antarctica"
    if lat < 0 and lng > 0:
        return "Australia/Asia"
    if lat < 0 and lng < 0:
        return "South America"
    if lat > 0 and lng < -30:
        return "North America"
    return "Europe/Asia"

# =========================
# EXTRACT
# =========================
def extract_users():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        logging.info("API data extracted successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API extraction failed: {e}")
        raise

# =========================
# TRANSFORM & CLEAN
# =========================
def transform_users(raw_users):
    transformed = []

    for user in raw_users:
        lat = float(user.get("address", {}).get("geo", {}).get("lat", 0))
        lng = float(user.get("address", {}).get("geo", {}).get("lng", 0))

        company_name = user.get("company", {}).get("name", "")
        parent_company = company_name.split("-")[0].split()[0] if company_name else None

        email = user.get("email")
        website = user.get("website")

        transformed.append({
            "user_id": user.get("id"),
            "name": user.get("name"),
            "email": email,
            "email_domain": email.split("@")[1] if email and "@" in email else None,
            "city": user.get("address", {}).get("city"),
            "zipcode": user.get("address", {}).get("zipcode"),
            "latitude": lat,
            "longitude": lng,
            "continent": infer_continent(lat, lng),
            "hemisphere": "Northern" if lat >= 0 else "Southern",
            "company": company_name,
            "parent_company": parent_company,
            "website_tld": website.split(".")[-1] if website else None,
            "created_at": datetime.utcnow().isoformat()
        })

    logging.info("Data transformation completed")
    return transformed

# =========================
# VALIDATION
# =========================
def validate_users(users):
    seen_ids = set()
    valid_users = []
    rejected_users = []

    for user in users:
        reasons = []

        if user["user_id"] in seen_ids:
            reasons.append("Duplicate user_id")
        if not user["email"] or "@" not in user["email"]:
            reasons.append("Invalid email")
        if not user["city"]:
            reasons.append("City is null")
        if not user["zipcode"] or len(str(user["zipcode"])) < 5:
            reasons.append("Invalid zipcode")

        if reasons:
            user["rejection_reason"] = "; ".join(reasons)
            rejected_users.append(user)
            logging.warning(f"Rejected user {user['user_id']}: {reasons}")
        else:
            seen_ids.add(user["user_id"])
            valid_users.append(user)

    logging.info(
        f"Validation completed: {len(valid_users)} valid, {len(rejected_users)} rejected"
    )
    return valid_users, rejected_users

# =========================
# SAVE CSV
# =========================
def save_csv(filename, data):
    if not data:
        return

    headers = list(data[0].keys())

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    logging.info(f"CSV saved: {filename}")

# =========================
# DATABASE
# =========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            email_domain TEXT,
            city TEXT,
            zipcode TEXT,
            latitude REAL,
            longitude REAL,
            continent TEXT,
            hemisphere TEXT,
            company TEXT,
            parent_company TEXT,
            website_tld TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    logging.info("Database initialized")

def insert_users(users):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT OR REPLACE INTO users
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            u["user_id"],
            u["name"],
            u["email"],
            u["email_domain"],
            u["city"],
            u["zipcode"],
            u["latitude"],
            u["longitude"],
            u["continent"],
            u["hemisphere"],
            u["company"],
            u["parent_company"],
            u["website_tld"],
            u["created_at"]
        ) for u in users
    ])

    conn.commit()
    conn.close()
    logging.info(f"Inserted {len(users)} records into database")

# =========================
# SQL INSIGHTS
# =========================
def run_sql_insights():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("\n📊 BUSINESS INSIGHTS\n")

    queries = {

        "Users by City": """
        SELECT city, COUNT(*)
        FROM users
        GROUP BY city
        ORDER BY COUNT(*) DESC
        """,

        "Users by Company": """
            SELECT company, COUNT(*)
            FROM users
            GROUP BY company
            ORDER BY COUNT(*) DESC
        """,

        "Users by Continent": """
            SELECT continent, COUNT(*) 
            FROM users
            GROUP BY continent
            ORDER BY COUNT(*) DESC
        """,
        "Users by Hemisphere": """
            SELECT hemisphere, COUNT(*) 
            FROM users
            GROUP BY hemisphere
        """,
        "Parent Company Concentration": """
            SELECT parent_company, COUNT(*) 
            FROM users
            GROUP BY parent_company
            HAVING COUNT(*) > 1
        """,
        "Email Domain Usage": """
            SELECT email_domain, COUNT(*) 
            FROM users
            GROUP BY email_domain
            ORDER BY COUNT(*) DESC
        """,
        "Website TLD Usage": """
            SELECT website_tld, COUNT(*) 
            FROM users
            GROUP BY website_tld
        """
    }

    for title, query in queries.items():
        print(f"\n{title}:")
        cursor.execute(query)
        for row in cursor.fetchall():
            print(row)

    conn.close()

# =========================
# PIPELINE EXECUTION
# =========================
def run_pipeline():
    logging.info("Pipeline started")

    raw_users = extract_users()
    transformed_users = transform_users(raw_users)
    valid_users, _ = validate_users(transformed_users)

    save_csv(CLEAN_CSV, valid_users)

    init_db()
    insert_users(valid_users)

    run_sql_insights()

    logging.info("Pipeline completed successfully")

if __name__ == "__main__":
    run_pipeline()
