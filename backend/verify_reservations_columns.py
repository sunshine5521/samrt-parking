import sqlite3

# Connect to the database
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# Get all columns from reservations table
cursor.execute('PRAGMA table_info(reservations)')
columns = cursor.fetchall()

# Print columns clearly
print("Reservations table columns:")
print("Index | Name | Type | Not Null | Default Value | Primary Key")
print("-----------------------------------------------------------------")
for col in columns:
    # Format the column information
    col_index = col[0]
    col_name = col[1]
    col_type = col[2]
    not_null = "YES" if col[3] else "NO"
    default_val = col[4] or "None"
    primary_key = "YES" if col[5] else "NO"
    
    # Print in a table format
    print(f"{col_index:5} | {col_name:20} | {col_type:10} | {not_null:7} | {default_val:15} | {primary_key:11}")

# Close the connection
conn.close()
