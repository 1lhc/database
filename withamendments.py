# Description: This script generates a SQLite database with applications, amendments, and STVPs.

import sqlite3
from faker import Faker
from datetime import datetime, timedelta
import random

# Connect to the database
connection = sqlite3.connect('with_amendments.db')
cursor = connection.cursor()

# Create schema
def create_schema(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            fin TEXT NOT NULL,
            name TEXT NOT NULL,
            pass_type TEXT NOT NULL,
            doa TEXT NOT NULL,
            company_uen TEXT NOT NULL,
            status TEXT NOT NULL,
            doe TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS amendments (
            amendment_id TEXT PRIMARY KEY,
            application_id TEXT NOT NULL,
            amendment_date TEXT NOT NULL,
            original_value TEXT NOT NULL,
            amended_value TEXT NOT NULL,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stvps (
            id TEXT PRIMARY KEY,
            application_id TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''')

# Recreate the schema
cursor.execute("DROP TABLE IF EXISTS applications")
cursor.execute("DROP TABLE IF EXISTS amendments")
create_schema(cursor)

# Initialize Faker
fake = Faker()
application_count = 20  # Testing dataset

# Generate applications
applications_data = []
amendments_data = []

# Generate applications and amendments
for app_index in range(2, application_count + 1):
    # Generate application details
    application_id = f"A{str(app_index).zfill(4)}"
    fin = fake.bothify(text='?#######?')
    name = fake.name()
    pass_type = random.choice(['Employment Pass', 'EntrePass', 'S Pass', 'Dependant’s Pass', 'Long-Term Visit Pass'])
    doa = fake.date_between(start_date='-5y', end_date='today').isoformat()  # 2019 to today
    company_uen = fake.bothify(text='UEN#####')
    status = random.choice(['Pending', 'Approved', 'Rejected', 'Withdrawn', 'Cancelled', 'Issued'])
    doe = (datetime.strptime(doa, '%Y-%m-%d') + timedelta(days=365 * random.randint(1, 5))).strftime('%Y-%m-%d')  # 1-5 years after doa
    applications_data.append((application_id, fin, name, pass_type, doa, company_uen, status, doe))

    # Generate amendments
    amendment_count = random.randint(0, 3)
    last_amend_date = datetime.strptime(doa, '%Y-%m-%d')
    for amend_index in range(1, amendment_count + 1):
        last_amend_date += timedelta(weeks=random.randint(2, 4))
        if last_amend_date >= datetime.strptime(doe, '%Y-%m-%d'):
            break
        amendment_id = f"P{str(amend_index).zfill(2)}{application_id}"
        amendment_date = last_amend_date.strftime('%Y-%m-%d %H:%M:%S')
        original_value = doe
        amended_value = (datetime.strptime(original_value, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d')
        amendments_data.append((amendment_id, application_id, amendment_date, original_value, amended_value))
        doe = amended_value  # Update doe after amendment

    # Update the final doe in applications
    applications_data[-1] = (*applications_data[-1][:-1], doe)  # Update in-memory
    cursor.execute("UPDATE applications SET doe = ? WHERE id = ?", (doe, application_id))

    # Generate STVPs for expired passes
    stvps_data = []
    current_date = datetime.now().date()
    for app_id, _, _, _, _, _, _, doe in applications_data:
        if datetime.strptime(doe, '%Y-%m-%d').date() < current_date:
            stvp_id = f"STVP{app_id[1:]}"
            start_date = (datetime.strptime(doe, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.strptime(doe, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d')
            stvps_data.append((stvp_id, app_id, start_date, end_date))

# Add the test application last
applications_data.append((
        "A0001",                    # ID
        "S1234567X",                # FIN (the test value)
        "Test User",                # Name
        "Employment Pass",          # Pass type
        (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),  # DOA (30 days ago)
        "UEN12345",                 # Company UEN
        "Pending",                  # Status
        (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')  # DOE (expired)
    ))

# Ensure all IDs are unique
ids = [app[0] for app in applications_data]
if len(ids) != len(set(ids)):
    raise ValueError("Duplicate IDs found in applications_data")

# Insert applications
cursor.executemany('''
    INSERT INTO applications (id, fin, name, pass_type, doa, company_uen, status, doe)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', applications_data)

# Insert amendments
cursor.executemany('''
    INSERT INTO amendments (amendment_id, application_id, amendment_date, original_value, amended_value)
    VALUES (?, ?, ?, ?, ?)
''', amendments_data)

# Insert STVPs
cursor.executemany('''
    INSERT INTO stvps (id, application_id, start_date, end_date)
    VALUES (?, ?, ?, ?)
''', stvps_data)

# Commit and close
connection.commit()
connection.close()

print(f"{len(applications_data)} applications and {len(amendments_data)} amendments added.")
print(f"{len(stvps_data)} STVPs added.")