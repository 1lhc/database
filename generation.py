import sqlite3
from faker import Faker
import random
from datetime import timedelta

# Connect to the database and create the updated schema
connection = sqlite3.connect('synthetic_wins.db')
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
            doe TEXT  -- Only applicable for "Issued" applications
        )
    ''')

# Recreate the schema
cursor.execute("DROP TABLE IF EXISTS applications")  # Drop table to start fresh
create_schema(cursor)

# Initialize Faker and set parameters
fake = Faker()
application_count = 100  # Start with a smaller number for testing

# Generate synthetic data
fins = set()  # To keep track of unique FINs
data = []

for _ in range(application_count):
    # Ensure each FIN is unique
    while True:
        fin = fake.bothify(text='?#######?')
        if fin not in fins:
            fins.add(fin)
            break
    
    # Generate the common data for this FIN
    base_name = fake.name()
    pass_type = random.choice(['Employment Pass', 'EntrePass', 'S Pass', 'Dependant’s Pass', 'Long-Term Visit Pass'])
    company_uen = fake.bothify(text='UEN#####')

    # Decide whether to include a 'Pending' or 'Approved' application (or neither)
    if random.choice([True, False]):  # 50% chance to have neither "Pending" nor "Approved"
        if random.choice([True, False]):  # 50% chance for "Pending" if including either
            doa = fake.date_this_decade().isoformat()
            data.append((fin, base_name, pass_type, doa, company_uen, 'Pending', None))
        else:
            approved_doa = fake.date_this_decade().isoformat()
            doe = (fake.date_this_decade() + timedelta(days=random.randint(30, 365))).isoformat()
            data.append((fin, base_name, pass_type, approved_doa, company_uen, 'Approved', doe))
    
    # Add multiple applications with 'Rejected', 'Withdrawn', 'Cancelled', or 'Issued' statuses
    other_statuses = random.choices(['Rejected', 'Withdrawn', 'Cancelled', 'Issued'], k=random.randint(1, 5))
    
    for status in other_statuses:
        doa = fake.date_this_decade().isoformat()  # Unique doa for each application
        name_variation = ' '.join(reversed(base_name.split()))  # Simple name reversal for variation
        doe = None  # Expiry date only for "Issued" applications
        if status == 'Issued':
            doe = (fake.date_this_decade() + timedelta(days=random.randint(30, 365))).isoformat()
        
        data.append((fin, name_variation, pass_type, doa, company_uen, status, doe))

# Insert data into the applications table
cursor.executemany('''
    INSERT INTO applications (fin, name, pass_type, doa, company_uen, status, doe)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', data)

# Commit and close the connection
connection.commit()
connection.close()

print(f"{application_count} applications added for testing.")