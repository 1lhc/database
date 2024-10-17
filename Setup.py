import sqlite3
from datetime import datetime, timedelta

def create_schema(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fin TEXT NOT NULL,
                name TEXT NOT NULL,
                pass_type TEXT NOT NULL,
                doa TEXT NOT NULL,
                company_uen TEXT NOT NULL
                    )
    ''')

def insert_sample_data(cursor):
    # Insert sample applications
    applications = [
        ('FIN1', 'Name1', 'PassType1', '2020-01-01', 'UEN1'),
        ('FIN2', 'Name2', 'PassType2', '2020-02-02', 'UEN2')
    ]

    cursor.executemany('''
    INSERT INTO applications (fin, name, pass_type, doa, company_uen)
    VALUES (?, ?, ?, ?, ?)
    ''', applications)

def verify_data_insertion(cursor):
    cursor.execute('''
    SELECT * FROM applications WHERE fin = 'FIN1'
    ''')
    result = cursor.fetchone()
    if result:
        print(f"Data for FIN1 found: {result}")
    else:
        print("Data for FIN1 not found")

def main():
    conn = sqlite3.connect('mock_wins.db')
    cursor  = conn.cursor()

    create_schema(cursor)
    insert_sample_data(cursor)
    verify_data_insertion(cursor)

    # Commit the changes
    conn.commit()
    conn.close()

    print("Database setup completed.")

if __name__ == '__main__':
    main()