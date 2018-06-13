#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, url_for, render_template
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

app = Flask(__name__)

# Memory Data
# TASKSDATA = {
# 	{
# 		'id': 1,
# 		'title': 'Buy groceries',
# 		'description': 'Milk, Cheese, Pizza, Fruit, Tyleno',
# 		'done': False
# 	},
# 	{
# 		'id': 2,
# 		'title': 'Learn Python',
# 		'description': 'Need to find a good Python tutorial on the web',
# 		'done': False
# 	},
# 	{
# 		'id': 3,
# 		'title': 'Wedding',
# 		'description': 'wine, food, beer, apps, minister',
# 		'done': False
# 	}
# }

PRODUCTS = {
    'iphone': {
        'name': 'iPhone 5S',
        'category': 'Phones',
        'price': 699,
    },
    'galaxy': {
        'name': 'Samsung Galaxy 5',
        'category': 'Phones',
        'price': 649,
    },
    'ipad-air': {
        'name': 'iPad Air',
        'category': 'Tablets',
        'price': 649,
    },
    'ipad-mini': {
        'name': 'iPad Mini',
        'category': 'Tablets',
        'price': 549
    }
}

# Index.HTML
@app.route('/')
@app.route('/home/')
def index():
	return render_template('index.html', products=PRODUCTS)

@app.route('/product/<key>')
def detail(key):
	product = PRODUCTS.get(key)
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