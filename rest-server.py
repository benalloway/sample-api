#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, url_for, render_template
from flask_httpauth import HTTPBasicAuth
import csv

auth = HTTPBasicAuth()

app = Flask(__name__)

# Memory Data
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

@app.route('/')
@app.route('/home/')
def index():
	products = getDB().values()
	sortby = request.args.get('sortby')
	
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

@app.route('/product/<key>')
def detail(key):
	product = getDB().get(key)
	if not product:
		abort(404)
	return render_template('detail.html', product=product)


# 
# RESTful API stuff
# 


# Memory Data
tasks = [
	{
		'id': 1,
		'title': u'Buy groceries',
		'description': u'Milk, Cheese, Pizza, Fruit, Tyleno',
		'done': False
	},
	{
		'id': 2,
		'title': u'Learn Python',
		'description': u'Need to find a good Python tutorial on the web',
		'done': False
	},
	{
		'id': 3,
		'title': u'Wedding',
		'description': u'wine, food, beer, apps, minister',
		'done': False
	}
]



# Authentication, add "@auth.login_required" where needed
@auth.get_password
def get_password(username):
	if username == 'benalloway':
		return 'benisawesome'
	return None
@auth.error_handler
def unauthorized():
	return make_response(jsonify({'error': 'Unauthorized access'}), 401)


# returns public uri instead of id
def make_public_task(task):
	new_task = {}
	for field in task:
		if field == 'id':
			new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
		else:
			new_task[field] = task[field]
	return new_task


# GET list of tasks 
@app.route('/todo/api/v1.0/tasks/', methods=['GET'])
@auth.login_required
def get_tasks():
	return jsonify({'tasks': [make_public_task(task) for task in tasks]})


# POST new list data
@app.route('/todo/api/v1.0/tasks/', methods=['POST'])
@auth.login_required
def create_task():
	if not request.json or not 'title' in request.json:
		abort(400)
	task = {
		'id': tasks[-1]['id'] + 1,
		'title': request.json['title'],
		'description': request.json.get('description', ""),
		'done':False
	}
	tasks.append(task)
	return jsonify({'task': task}), 201


# GET individual task by id
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	return jsonify({'task':task[0]})


# PUT, update individual task by id
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	if not request.json:
		abort(400)
	if 'title' in request.json and type(request.json['title']) != unicode:
		abort(400)
	if 'description' in request.json and type(request.json['description']) is not unicode:
		abort(400)
	if 'done' in request.json and type(request.json['done']) is not bool:
		abort(400)
	task[0]['title'] = request.json.get('title', task[0]['title'])
	task[0]['description'] = request.json.get('description', task[0]['description'])
	task[0]['done'] = request.json.get('done', task[0]['done'])
	return jsonify({'task':task[0]})


# DELETE, individual task by id
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	tasks.remove(task[0])
	return jsonify({'result': True})

# Throw 404, resource not found, if no id exists.
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

# End File
if __name__ == '__main__':
	app.run(debug=True)