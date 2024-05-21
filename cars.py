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
            return [table['name'] for table in tables if table['name'] != 'sqlite_sequence'] # Returning a list of table names by iterating over the tables list and extracting the value associated with the key 'name'. We are also filtering out the 'sqlite_sequence' table which is not relevant to end-users. 
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
        

#---------------------------- Functions for customers specifically ---------------------------- 

def get_customers(brand=None, dealer=None, purchase_price=None, model=None):
    conn = create_connection()
    query = """
        SELECT Customers.* FROM Customers
        JOIN Customer_Ownership ON Customers.customer_id = Customer_Ownership.customer_id
        JOIN Car_Vins ON Customer_Ownership.vin = Car_Vins.vin
        JOIN Models ON Car_Vins.model_id = Models.model_id
        JOIN Brands ON Models.brand_id = Brands.brand_id
        JOIN Dealers ON Customer_Ownership.dealer_id = Dealers.dealer_id
        WHERE 1=1
    """
    params = {}
    if brand:
        query += " AND Brands.brand_name = :brand"
        params['brand'] = brand
    if dealer:
        query += " AND Dealers.dealer_name = :dealer"
        params['dealer'] = dealer
    if purchase_price:
        query += " AND Customer_Ownership.purchase_price > :purchase_price"
        params['purchase_price'] = purchase_price
    if model:
        query += " AND Models.model_name = :model"
        params['model'] = model

    try:
        cur = conn.cursor()
        cur.execute(query, params)
        customers = cur.fetchall()
        return [dict(row) for row in customers]
    except sqlite3.Error as e:
        print(f"Error fetching customers: {e}")
        return []
    finally:
        conn.close()
        
def get_customer_by_id(customer_id):
    conn = create_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Customers WHERE customer_id = ?", (customer_id,)) # The second argument to cur.execute is a tuple containing the actual value to replace the ? placeholder in the SQL statement
        customer = cur.fetchone()
        return dict(customer) if customer else None
    except sqlite3.Error as e:
        print(f"Error fetching customer by ID: {e}")
        return None
    finally:
        conn.close()

def add_customer(customer):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            columns = ', '.join(customer.keys()) # customer.keys() are the column names in CUSTOMERS table
            placeholders = ', '.join(['?'] * len(customer)) # len(customer) is equal to the number of columns in CUSTOMERS table
            sql = f"INSERT INTO Customers ({columns}) VALUES ({placeholders})"
            cur.execute(sql, tuple(customer.values())) # The ? placeholders in the SQL string are replaced by the values in the tuple in the correct order
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding customer: {e}")
        finally:
            conn.close()

def update_customer(customer_id, customer):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in customer.keys()]) # Customer keys are simply column names
            sql = f"UPDATE Customers SET {set_clause} WHERE customer_id = ?"
            values = list(customer.values()) # Converting the dictionary values to a list
            values.append(customer_id) # Adding the customer_id to the end of the list of values
            cur.execute(sql, values) # Executing the SQL UPDATE statement. The ? placeholders in the SQL string are replaced by the values in the values list in the correct order
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating customer: {e}")
        finally:
            conn.close()

def delete_customer(customer_id):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM Customers WHERE customer_id = ?", (customer_id,)) # The second argument to cur.execute is a tuple containing the actual value to replace the ? placeholder in the SQL statement
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting customer: {e}")
        finally:
            conn.close()
            
#---------------------------- Functions for car models specifically #----------------------------

def get_models(car_color=None, brand=None, price=None):
    conn = create_connection()
    query = """
    SELECT * FROM Models
    JOIN Car_Options ON Models.model_id=Car_Options.model_id
    JOIN Brands ON Brands.brand_id=Models.brand_id
    WHERE 1=1
    """
    params = {}
    if car_color:
        query += " AND Car_Options.color = :car_color"
        params['car_color'] = car_color
    if brand:
        query += " AND Brands.brand_name = :brand"
        params['brand'] = brand
    if price:
        query += " AND Models.model_base_price <= :price"
        params['price'] = price

    query += " GROUP BY Models.model_id"  # Grouping by model_id to aggregate colors

    try:
        cur = conn.cursor()
        cur.execute(query, params)
        models = cur.fetchall()
        # Converting 'colors' from comma-separated string to a list:
        for model in models:
            model['possible_colors'] = model['possible_colors'].split(',') if model['possible_colors'] else []
        return [dict(row) for row in models]
    except sqlite3.Error as e:
        print(f"Error fetching models: {e}")
        return []
    finally:
        conn.close()

def get_model_colors_by_id(model_id):
    conn = create_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT Models.*, GROUP_CONCAT(Car_Options.color) as colors FROM Models JOIN Car_Options ON Models.model_id=Car_Options.model_id WHERE Models.model_id = ?", (model_id,))
        model = cur.fetchone()
        if model:
            model = dict(model)
            model['possible_colors'] = model['possible_colors'].split(',') if model['possible_colors'] else []
        return model
    except sqlite3.Error as e:
        print(f"Error fetching model by ID: {e}")
        return None
    finally:
        conn.close()

def add_model(model):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            columns = ', '.join(model.keys())  # Creating the columns part of the SQL statement
            placeholders = ', '.join(['?'] * len(model))  # Creating the placeholders part of the SQL statement
            sql = f"INSERT INTO Models ({columns}) VALUES ({placeholders})"  # Combining into a full SQL statement
            cur.execute(sql, tuple(model.values()))  # Executing the SQL statement with the actual values
            conn.commit()  # Commiting the transaction
        except sqlite3.Error as e:
            print(f"Error adding model: {e}")
        finally:
            conn.close()  # Ensuring the connection is closed

def update_model(model_id, model):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in model.keys()])  # Creating the SET part of the SQL statement
            sql = f"UPDATE Models SET {set_clause} WHERE model_id = ?"  # Combining into a full SQL statement
            values = list(model.values())  # Converting the dictionary values to a list
            values.append(model_id)  # Adding the model_id to the list of values
            cur.execute(sql, values)  # Executing the SQL statement with the actual values
            conn.commit()  # Commiting the transaction
        except sqlite3.Error as e:
            print(f"Error updating model: {e}")
        finally:
            conn.close()

def delete_model(model_id):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM Models WHERE model_id = ?", (model_id,))  # Executing the DELETE statement with the model_id
            conn.commit()  # Commiting the transaction
        except sqlite3.Error as e:
            print(f"Error deleting model: {e}")
        finally:
            conn.close() 