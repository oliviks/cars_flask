# Task origins: final project from the course "Python Applications' at Kozminski University.

## Requests & Flask
 
Develop a basic Flask server that utilizes a database created with the SQLite Sample Database (available at https://github.com/dtaivpp/car_company_database). You can find a tutorial on integrating Flask with SQLite at https://pythonbasics.org/flask-sqlite/.
 
The server should expose API endpoints that allow user to retrieve, save, edit and remove data. For example, you could create endpoints that retrieve all customers that bought Ferrari from Priority X dealer and paid more than 20000$. Allow user to create new rows of data using POST method, update it with PUT method and delete it with DELETE method. 
Required endpoints to handle:
 
CRUD for customers with filtering (search parameters: brand, dealer, purchase price, model)
CRUD for models with filtering - display possible colors for each model (search parameters: car color, brand, price)
 
None of the filtering parameter are required to perform request, they are optional and only for narrowing results
If no results are found return empty list of items
Return responses in JSON format.
