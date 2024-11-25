import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta

# Connect to the database and create updated schema
connection = sqlite3.connect('with_amendments.db')
cursor = connection.cursor()

def create_schema(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fin TEXT NOT NULL,
            name TEXT NOT NULL,
            pass_type TEXT NOT NULL,
            doa TEXT NOT NULL,
            company_uen TEXT NOT NULL,
            status TEXT NOT NULL,
            doe TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS amendments (
            amendment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            amendment_date TEXT NOT NULL,
            field_amended TEXT NOT NULL,
            original_value TEXT NOT NULL,
            amended_value TEXT NOT NULL,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''')

# Recreate the schema
cursor.execute("DROP TABLE IF EXISTS applications")
cursor.execute("DROP TABLE IF EXISTS amendments")
create_schema(cursor)

# Initialize Faker
fake = Faker()
application_count = 50  # Small sample size for testing

# Generate synthetic applications data
applications_data = []
amendments_data = []

for _ in range(application_count):
    fin = fake.bothify(text='?#######?')
    name = fake.name()
    pass_type = random.choice(['Employment Pass', 'EntrePass', 'S Pass', 'Dependant’s Pass', 'Long-Term Visit Pass'])
    doa = fake.date_this_decade().isoformat()
    company_uen = fake.bothify(text='UEN#####')
    status = random.choice(['Pending', 'Approved', 'Rejected', 'Withdrawn', 'Cancelled', 'Issued'])
    doe = None if status != 'Issued' else (fake.date_this_decade() + timedelta(days=random.randint(30, 365))).isoformat()
    applications_data.append((fin, name, pass_type, doa, company_uen, status, doe))

# Insert applications into the database
cursor.executemany('''
    INSERT INTO applications (fin, name, pass_type, doa, company_uen, status, doe)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', applications_data)

# Fetch application IDs to link amendments
cursor.execute('SELECT id FROM applications')
application_ids = [row[0] for row in cursor.fetchall()]

# Generate synthetic amendments data
for application_id in application_ids:
    for _ in range(random.randint(0, 3)):  # 0 to 3 amendments per application
        amendment_date = fake.date_time_this_decade().isoformat()
        field_amended = random.choice(['status', 'name', 'company_uen', 'doa', 'doe'])
        original_value = fake.word() if field_amended != 'status' else random.choice(['Pending', 'Approved', 'Rejected', 'Withdrawn', 'Cancelled', 'Issued'])
        amended_value = fake.word() if field_amended != 'status' else random.choice(['Pending', 'Approved', 'Rejected', 'Withdrawn', 'Cancelled', 'Issued'])
        amendments_data.append((application_id, amendment_date, field_amended, original_value, amended_value))

# Insert amendments into the database
cursor.executemany('''
    INSERT INTO amendments (application_id, amendment_date, field_amended, original_value, amended_value)
    VALUES (?, ?, ?, ?, ?)
''', amendments_data)

# Commit and close the connection
connection.commit()
connection.close()

print(f"{len(applications_data)} applications and {len(amendments_data)} amendments added.")