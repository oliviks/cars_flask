from flask import Flask, render_template, request, redirect, url_for, flash
import cars

app = Flask(__name__)

primary_key_columns = {
    'Customers': 'customer_id',
    'Models': 'model_id',
    'Customer_Ownership': 'customer_id',
    'Dealer_Brand': 'dealer_id',
    'Car_Parts': 'part_id',
    'Manufacture_Plant': 'manufacture_plant_id',
    'Brands': 'brand_id',
    'Dealers': 'dealer_id',
    'Car_Options': 'option_set_id',
    'Car_Vins': 'vin'
}

@app.route('/')
def index():
    table_names = cars.get_table_names()
    return render_template('index.html', table_names=table_names)

@app.route('/table/<table_name>')
def display_table_data(table_name):
    data = cars.get_table_data(table_name)
    table_names = cars.get_table_names()
    return render_template('table_data.html', table_names=table_names, table_name=table_name, data=data)

# GET: Used to request data from a specified resource. GET requests should only retrieve data and have no other effect.
# POST: Used to send data to a server to create or update a resource. The data sent to the server with POST is stored in the request body.
@app.route('/add_data', methods=['GET', 'POST'])
def add_data():
    table_names = cars.get_table_names()
    if request.method == 'POST':
        selected_table = request.form.get('table_name')
        return redirect(url_for('add_table_record', table_name=selected_table))
    return render_template('add_data.html', table_names=table_names)

@app.route('/add_data/<table_name>', methods=['GET', 'POST'])
def add_table_record(table_name):
    data = cars.get_table_data(table_name)
    if request.method == 'POST':
        record = request.form.to_dict()
        cars.add_record(table_name, record)
        return redirect(url_for('display_table_data', table_name=table_name))
    return render_template('add_record.html', table_name=table_name, data=data)

@app.route('/edit_data', methods=['GET', 'POST'])
def select_edit_data():
    table_names = cars.get_table_names()
    if request.method == 'POST':
        table_name = request.form.get('table_name')
        record_id = request.form.get('record_id')
        return redirect(url_for('edit_data', table_name=table_name, record_id=record_id))
    return render_template('edit_data_selection.html', table_names=table_names)

# Ensuring that the PK IDs remain unchanged - read-only (see: edit_data.html)
@app.route('/edit_data/<table_name>/<record_id>', methods=['GET', 'POST'])
def edit_data(table_name, record_id):
    if request.method == 'GET':
        record = cars.get_record_by_id(table_name, record_id, primary_key_columns)
        if record:
            return render_template('edit_data.html', record=record, table_name=table_name, record_id=record_id, primary_key_columns=primary_key_columns)
        else:
            return "Record not found", 404
    elif request.method == 'POST':
        updated_record = request.form.to_dict()
        if cars.update_record(table_name, primary_key_columns[table_name], record_id, updated_record):
            return redirect(url_for('display_table_data', table_name=table_name))
        else:
            return "Error updating record", 500  # Internal Server Error

@app.route('/update_record/<table_name>/<record_id>', methods=['POST'])
def update_record_route(table_name, record_id):
    updated_record = request.form.to_dict()
    if cars.update_record(table_name, primary_key_columns[table_name], record_id, updated_record):
        return redirect(url_for('display_table_data', table_name=table_name))
    else:
        return "Error updating record", 500  # Internal Server Error

# In delete_row.html, we ensured that a confirmation pop-up for record deletion appears
@app.route('/delete_data', methods=['GET', 'POST'])
def delete_data():
    if request.method == 'POST':
        selected_table = request.form.get('table_name')
        record_id = request.form.get('record_id')
        primary_key_column = primary_key_columns.get(selected_table)

        if cars.delete_record(selected_table, primary_key_column, record_id):
            delete_message = f"Row with ID {record_id} has been deleted successfully!"
        else:
            delete_message = "Error deleting row!"

        table_names = cars.get_table_names()
        return render_template('delete_row.html', table_names=table_names, delete_message=delete_message)

    table_names = cars.get_table_names()
    return render_template('delete_row.html', table_names=table_names)


@app.route('/filter_data', methods=['GET', 'POST'])
def filter_data():
    table_names = cars.get_table_names()
    results = []

    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        model_name = request.form.get('model_name')
        model_price = request.form.get('model_price')
        dealer_name = request.form.get('dealer_name')

        # Custom SQL query to filter data based on provided inputs
        query = """
            SELECT Customers.first_name, Customers.last_name
            FROM Customers
            JOIN Customer_Ownership ON Customers.customer_id = Customer_Ownership.customer_id
            JOIN Car_Vins on Customer_Ownership.vin=Car_Vins.vin
            JOIN Models ON Car_Vins.model_id = Models.model_id
            JOIN Dealers ON Customer_Ownership.dealer_id = Dealers.dealer_id
            WHERE 1=1
        """
        params = {}

        if customer_name:
            query += " AND Customers.first_name LIKE :customer_name"
            params['customer_name'] = f'%{customer_name}%'
        if model_name:
            query += " AND Models.model_name LIKE :model_name"
            params['model_name'] = f'%{model_name}%'
        if model_price:
            query += " AND Customer_Ownership.purchase_price > :model_price"
            params['model_price'] = model_price
        if dealer_name:
            query += " AND Dealers.dealer_name LIKE :dealer_name"
            params['dealer_name'] = f'%{dealer_name}%'

        # Execute the query
        results = cars.execute_custom_query(query, params)

    return render_template('filter_data.html', table_names=table_names, results=results)

########################################################
# CRUD for Customers
@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if request.method == 'GET':
        brand = request.args.get('brand')
        dealer = request.args.get('dealer')
        purchase_price = request.args.get('purchase_price')
        model = request.args.get('model')
        customers = cars.get_customers(brand, dealer, purchase_price, model)
        return render_template('customers.html', customers=customers)
    elif request.method == 'POST':
        data = request.form.to_dict()
        cars.add_customer(data)
        return redirect(url_for('customers'))

@app.route('/customers/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        data = request.form.to_dict()
        cars.add_customer(data)
        return redirect(url_for('customers'))
    return render_template('add_customer.html')

@app.route('/customers/<int:customer_id>', methods=['GET', 'POST'])
def customer_detail(customer_id):
    if request.method == 'GET':
        customer = cars.get_customer_by_id(customer_id)
        return render_template('edit_customer.html', customer=customer)
    elif request.method == 'POST':
        data = request.form.to_dict()
        cars.update_customer(customer_id, data)
        return redirect(url_for('customers'))

@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    cars.delete_customer(customer_id)
    return redirect(url_for('customers'))

# CRUD for Models
@app.route('/models', methods=['GET', 'POST'])
def models():
    if request.method == 'GET':
        car_color = request.args.get('car_color')
        brand = request.args.get('brand')
        price = request.args.get('price')
        models = cars.get_models(car_color, brand, price)
        return render_template('models.html', models=models)
    elif request.method == 'POST':
        data = request.form.to_dict()
        cars.add_model(data)
        return redirect(url_for('models'))

@app.route('/models/add', methods=['GET', 'POST'])
def add_model():
    if request.method == 'POST':
        data = request.form.to_dict()
        cars.add_model(data)
        return redirect(url_for('models'))
    return render_template('add_model.html')

@app.route('/models/<int:model_id>', methods=['GET', 'POST'])
def model_detail(model_id):
    if request.method == 'GET':
        model = cars.get_model_colors_by_id(model_id)
        return render_template('edit_model.html', model=model)
    elif request.method == 'POST':
        data = request.form.to_dict()
        cars.update_model(model_id, data)
        return redirect(url_for('models'))

@app.route('/models/delete/<int:model_id>', methods=['POST'])
def delete_model(model_id):
    cars.delete_model(model_id)
    return redirect(url_for('models'))

if __name__ == '__main__':
    app.run(debug=True)
