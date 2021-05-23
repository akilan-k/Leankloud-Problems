from flask import Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
from dateutil.parser import parse
import mysql.connector

todo_database = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="todo",
  auth_plugin='mysql_native_password'
)

cur = todo_database.cursor(dictionary=True)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
)

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due': fields.DateTime(required=True, description='Due date in the format'),
    'status': fields.String(required=True, description='Status of the task')
})


class TodoDAO(object):
    def __init__(self):
    	cursorObj = todo_database.cursor()
    	cursorObj.execute('SELECT IFNULL(max(id),0) FROM todo_list;')
    	rs = cursorObj.fetchone()
    	self.counter = rs[0]

    def get(self, id):
        sql = "SELECT * FROM todo_list WHERE id=" + str(id)
        cur.execute(sql)
        todo = cur.fetchone()
        if todo != None:
        	return todo
        api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        todo = data
        todo['id'] = self.counter = self.counter + 1
        sql = "INSERT INTO todo_list VALUES (%s, %s, %s, %s)"
        val = (todo['id'], todo['task'], str(parse(str(todo['due'])[0:19])), todo['status'])
        cur.execute(sql, val)
        todo_database.commit()
        return todo

    def update(self, id, data):
    	todo = data
    	todo['id'] = id
    	sql = "UPDATE todo_list SET task=%s, due=%s, status=%s WHERE id=%s"
    	val = (todo['task'], str(parse(str(todo['due'])[0:19])), todo['status'], id)
    	cur.execute(sql, val)
    	todo_database.commit()
    	return todo

    def delete(self, id):
        sql = "DELETE FROM todo_list WHERE id=" + str(id)
        cur.execute(sql)
        todo_database.commit()
        
    def updateStatus(self, id, status):
    	todo = self.get(id)
    	todo['status'] = status
    	sql = "UPDATE todo_list SET status=%s WHERE id=%s"
    	val = (status, id)
    	cur.execute(sql, val)
    	todo_database.commit()
    	return todo
    	
    def dueTasks(self, date):
    	return [todo for todo in self.todos if str(todo['due'])[0:10] == date]
    	


DAO = TodoDAO()


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
    	'''List all the tasks'''
    	cur.execute("SELECT * FROM todo_list")
    	return cur.fetchall()
        
    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204
        
    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)
        
@ns.route('/<int:id>/<string:status>')
class TodoUpdateStatus(Resource):
    '''Lets you update the status of a task'''
    @ns.marshal_with(todo)
    def put(self, id, status):
        '''Update a tasks status given its identifier'''
        return DAO.updateStatus(id, status)

@ns.route('/due/<string:due_date>')
class ToDoDue(Resource):
    '''Shows the list of tasks which are due to be finished on that specified date'''
    @ns.marshal_with(todo)
    def get(self, due_date):
        '''Shows the list of tasks which are due to be finished on that specified date'''
        sql = "SELECT * FROM todo_list WHERE DATE(due)='" + due_date + "'"
        cur.execute(sql)
        return cur.fetchall()

@ns.route('/overdue')
class ToDoOverdue(Resource):
    '''Shows the list of tasks which are overdue'''
    @ns.marshal_with(todo)
    def get(self):
        '''Shows the list of tasks which are overdue'''
        sql = "SELECT * FROM todo_list WHERE DATE(due) < DATE(NOW()) AND status<>'Finished'"
        cur.execute(sql)
        return cur.fetchall()

@ns.route('/finished')
class ToDoFinished(Resource):
    '''Shows the list of tasks which are finished'''
    @ns.marshal_with(todo)
    def get(self):
        '''Shows the list of tasks which are finished'''
        sql = "SELECT * FROM todo_list WHERE status='Finished'"
        cur.execute(sql)
        return cur.fetchall()

if __name__ == '__main__':
    app.run(debug=True)
