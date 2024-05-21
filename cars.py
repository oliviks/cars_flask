import sqlite3
import os

# Ensuring the correct path to the database
DATABASE = os.path.join(os.path.dirname(__file__), 'car_company_database-master', 'Car_Database.db')

# ---------------------------- Defining a new function named 'create_connection' ----------------------------
def create_connection():
    # Starting the 'try' block
    try:
        conn = sqlite3.connect(DATABASE) # Establishing a connection to the SQLite db using the sqlite3.connect() function
        conn.row_factory = sqlite3.Row  # This allows us to get results as dictionaries, where the column names are used as keys
        return conn # Returning the connection object
    # Starting the 'except' block
    except sqlite3.Error as e: # Catching any exceptions of type sqlite3.Error that occur within the try block (and stroing in the 'e' variable)
        print(f"Error connecting to database: {e}") # Printing an error message to the console
        return None # Returning 'None' if db connection is not established

# ---------------------------- Defining a new function named 'get_table_names' ----------------------------
def get_table_names():
    conn = create_connection()
    if conn: # Checking if the connection was successfully established -> If conn is not None, the block of code under this condition is executed
        try:
            cur = conn.cursor() # Calling the cursor() method on the connection object to execute SQL commands and fetch results from the database
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';") # Executing an SQL query that retrieves the names of all tables in the db
            tables = cur.fetchall() # Fetching all results of the query and assigning them to the 'tables' variable. Each result is a row represented as a dictionary.
            return [table['name'] for table in tables] # Returning a list of table names by iterating over the tables list and extracting the value associated with the key 'name'
        except sqlite3.Error as e:
            print(f"Error fetching table names: {e}")
            return [] # Returning an empty list if an exception occurs
        finally: # Starting a 'finally' block 
            conn.close() # Ensuring that the connection is properly closed after the operation is complete, regardless of whether an exception occurs
    else: # If 'conn' is 'None' ...
        return [] # ... Returning an empty list if the connection is not established

# ---------------------------- Defining a new function named 'get_table_data' ----------------------------
def get_table_data(table_name):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table_name};") # Executing an SQL query that retrieves all the data from the specified table
            data = cur.fetchall()
            return [dict(row) for row in data] # Returning a list of dictionaries, where each dictionary represents a row from the table
        except sqlite3.Error as e:
            print(f"Error fetching data from table: {e}")
            return []
        finally:
            conn.close()
    else:
        return []


# ---------------------------- Defining a new function named 'add_record' ----------------------------
# record - a dictionary representing the data to be inserted (column_name:value)
def add_record(table_name, record):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            columns = ', '.join(record.keys()) # Creating a string of column names by joining the keys of the record dictionary with commas
            placeholders = ', '.join(['?'] * len(record)) # Creating a string of placeholders (?) for the values to be inserted. The number of placeholders matches the number of items in the record dictionary. These placeholders are replaced by the actual values during the execution of the SQL statement
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})" # Inserting the specified values into the specified columns of the specified table
            cur.execute(sql, tuple(record.values())) # Executing the SQL INSERT statement. The tuple(record.values()) converts the values of the record dictionary to a tuple, which is used to replace the placeholders in the SQL statement with the actual values
            conn.commit() # Saving the changes to the databas
        except sqlite3.Error as e:
            print(f"Error adding record: {e}")
        finally:
            conn.close()

# ---------------------------- Defining a new function named 'get_max_id' ----------------------------
def get_max_id(table_name):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM {table_name};") # Executing an SQL query that counts the number of rows in the specified table
            max_id = cur.fetchone()[0] # Fetching the result of the query using the fetchone() method, which returns a single row. Since the query returns a single value (the count of rows), it is accessed with [0] and assigned to the variable max_id
            return max_id # Returning the count of rows in the table
        except sqlite3.Error as e:
            print(f"Error fetching max ID from table: {e}")
            return None
        finally:
            conn.close()
    else:
        return None

# ---------------------------- Defining a new function named 'delete_record' ----------------------------
def delete_record(table_name, primary_key_column, record_id):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {table_name} WHERE {primary_key_column} = ?;", (record_id,)) # (record_id,): a tuple containing the value to be used in place of the ? placeholder in the SQL statement.
            conn.commit()
            return True # Returning True, if the record is successfully deleted.
        except sqlite3.Error as e:
            print(f"Error deleting record: {e}")
            return False
        finally:
            conn.close()
    else:
        return False


# ---------------------------- Defining a new function named 'get_record_by_id' ----------------------------
def get_record_by_id(table_name, record_id, primary_key_columns): # primary_key_columns: a dictionary where the keys are table names and the values are the corresponding primary key column names
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            if not isinstance(primary_key_columns, dict): # Checking if the primary_key_columns parameter is a dictionary. If it is not, an error message is printed and the function returns None.
                print("Error: primary_key_columns must be a dictionary.")
                return None
            
            primary_key_column = primary_key_columns.get(table_name) # Retrieving the primary key column name for the specified table from the primary_key_columns dictionary
            if not primary_key_column:
                print(f"No primary key column found for table: {table_name}")
                return None
            
            cur.execute(f"SELECT * FROM {table_name} WHERE {primary_key_column} = ?;", (record_id,))
            record = cur.fetchone() # Fetching the result of the query using the fetchone() method, which returns a single row. If no matching record is found - returning 'None'
            if record:
                return dict(record) # Converting the row to a dictionary and returning it 
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error fetching record by ID: {e}")
            return None
        finally:
            conn.close()
    else:
        return None


# ---------------------------- Defining a new function named 'update_record' ----------------------------

# updated_record: a dictionary containing the columns to be updated and their new values.
def update_record(table_name, primary_key_column, record_id, updated_record):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in updated_record.keys()]) # Creating a string that lists each column to be updated, with placeholders (?) for the new values. The join method is used to concatenate the key-value pairs with commas.
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key_column} = ?"
            values = list(updated_record.values()) # Extracting the values from the updated_record dictionary and converting them to a list
            values.append(record_id) # Appending the record_id to the 'values' list (to further replace "?" in 'WHERE {primary_key_column} = ?')
            print(f"Executing SQL: {sql}")  # Debug: print the SQL statement
            print(f"With values: {values}")  # Debug: print the values
            cur.execute(sql, values)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating record: {e}")
            return False
        finally:
            conn.close()
    else:
        return False


# ---------------------------- Defining a new function named 'get_custom_query_results' ----------------------------
def get_custom_query_results(query):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall() # where each row is initially represented as a sqlite3.Row object because of the row_factory setting
    conn.close()
    return results


# ---------------------------- Defining a new function named 'execute_custom_query' ----------------------------

# 'params' should be a tuple containing the values to be used in the query
def execute_custom_query(query, params):
    conn = create_connection()
    try:
        cursor = conn.execute(query, params)
        results = cursor.fetchall()
        return [dict(row) for row in results] # converting each row from the result set into a dictionary using a list comprehension
    finally:
        conn.close()