import sys
from flask import Flask
app = Flask(__name__)


@app.route('/')
@app.route('/catalogs/')
def catalogs():
	return sys._getframe().f_code.co_name

@app.route('/category/<int:category_id>/')
def showItemsForCategory(category_id):
	return sys._getframe().f_code.co_name

@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(category_id, item_id):
	return sys._getframe().f_code.co_name

@app.route('/category/<int:category_id>/addItem', methods=['GET', 'POST'])
def addItem(category_id):
	return sys._getframe().f_code.co_name

@app.route('/category/<int:category_id>/editItem/<int:item_id>/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
	return sys._getframe().f_code.co_name

@app.route('/category/<int:category_id>/deleteItem/<int:item_id>/', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
	return sys._getframe().f_code.co_name

@app.route('/gconnect', methods=['POST'])
def gconnect():
	return sys._getframe().f_code.co_name


@app.route('/gdisconnect')
def gdisconnect():
	return sys._getframe().f_code.co_name


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
