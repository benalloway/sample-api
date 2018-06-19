#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, url_for, render_template, redirect, Response
import csv

app = Flask(__name__)

# Memory Data Test Data
PRODUCTS = {
	'1': {
	    'name': 'iPhone 5S',
	    'category': 'Phones',
	    'price': 699,
	    'id': 1
	},
	'2': {
	    'name': 'Samsung Galaxy 5',
	    'category': 'Phones',
	    'price': 649,
	    'id': 2
	},
	'3': {
	    'name': 'iPad Air',
	    'category': 'Tablets',
	    'price': 649,
	    'id': 3
	},
	'4': {
	    'name': 'iPad Mini',
	    'category': 'Tablets',
	    'price': 549,
	    'id': 4
	}	
}


# 
# Easy Authentication
# add @requires_auth wherever you want authentication
# 

from functools import wraps

def check_auth(username, password):
	"""This function is called to check if a username / password combo is valid."""
	return username == 'admin' and password == 'password'

def authenticate():
	"""Sends a 401 response that enables basic auth"""
	return Response(
		'Could not verify your access level for that URL.\n'
		'You have to login with proper credentials', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return f(*args, **kwargs)
	return decorated

# 
# DB tools
# Version 1.0 
# description: version 1.0 is function based interaction with DB. version 1.1 will be updated to class based interaction with DB
# 

def writeDB(args=None):
	with open('database/products.csv', 'w') as dbfile:
		fieldnames = ['name', 'category', 'price', 'id']
		writer = csv.DictWriter(dbfile, fieldnames=fieldnames)
		writer.writeheader()
		for k,v in args.iteritems():
			writer.writerow(v)


def getDB(args=None):
	with open('database/products.csv') as dbfile:
		reader = csv.DictReader(dbfile)
		db = {}
		for row in reader:
			db[row['id']] = {'name':row['name'], 'category':row['category'], 'price':row['price'], 'id':row['id']}
		return db


def deleteDB(args=None):
	if args is not None:
		db = getDB()
		if args in db:
			del db[args]
			writeDB(db)


def postDB(args=None):
	if args is not None:
		db = getDB()
		data = args
		ids = []
		for k,v in db.iteritems():
			ids.append(v['id'])
		ids = [int(x) for x in ids]
		ids = max(ids) + 1
		data['id'] = str(ids)
		db[data['id']] = data
		writeDB(db)	


def putDB(args=None):
	if args is not None:
		db = getDB()
		if args['id'] in db:
			db[args['id']] = args
			writeDB(db)


# 
# List of Products, home page
# 

@app.route('/', methods=['POST', 'GET'])
@app.route('/products/', methods=['POST', 'GET'])
@requires_auth
def index():
	data = request.form.to_dict()

	# handle DELETE button
	if request.method == 'POST' and 'delete' in data:
		id = data['delete']
		deleteDB(id)
		return redirect('/')

	# fill data from CSV file
	products = getDB().values()

	# grab sortby GET data if any
	sortby = request.args.get('sortby')
	
	# Handle Sort by options 
	# sort by name a-z
	if sortby is not None and sortby == 'name':
		products = sorted(products, key=lambda product: product['name'].lower())
		return render_template('index.html', products=products)
	# sort by name z-a
	if sortby is not None and sortby == '-name':
		products = sorted(products, key=lambda product: product['name'].lower(), reverse=True)
		return render_template('index.html', products=products)
	# sort by id asc
	if sortby is not None and sortby == 'id':
		products = sorted(products, key=lambda product: int(product['id']))
		return render_template('index.html', products=products)
	# sort by id desc
	if sortby is not None and sortby == '-id':
		products = sorted(products, key=lambda product: int(product['id']), reverse=True)
		return render_template('index.html', products=products)
	# sort by ID asc
	else:
		return render_template('index.html', products=products)


# 
# Product Detail Page
# 

@app.route('/products/<key>', methods=['GET', 'POST'])
@requires_auth
def detail(key):
	# handle DELETE button
	if request.method == "POST":
		data = request.form.to_dict()
		if 'delete' in data:
			id = data['delete']
			deleteDB(id)
			return redirect('/')
		if 'update' in data:
			del data['update']
			putDB(data)
			product = getDB().get(key)
			return redirect('/')
	else:
		product = getDB().get(key)
		if not product:
			abort(404)
		return render_template('detail.html', product=product)


# 
# Create Product Page
# 


@app.route('/products/create/', methods=['GET', 'POST'])
@requires_auth
def create():
	if request.method == "POST":
		data = request.form.to_dict()
		print(data)
		postDB(data)
		return redirect('/')
	else:
		return render_template('create.html')


# Throw 404, resource not found, if no id exists.
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)


# End File
if __name__ == '__main__':
	app.run(debug=True)