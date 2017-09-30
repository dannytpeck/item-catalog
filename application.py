from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemlist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/categories/')
def show_categories():
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('categories.html', categories = categories)

@app.route('/categories/new/', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        new_category = Category(name = request.form['name'])
        session.add(new_category)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template('new_category.html')

@app.route('/categories/<int:category_id>/edit/', methods=['GET', 'POST'])
def edit_category(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
        session.add(category)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template('edit_category.html', category = category)

@app.route('/categories/<int:category_id>/delete/', methods=['GET', 'POST'])
def delete_category(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template('delete_category.html', category = category)

@app.route('/categories/<int:category_id>/new/', methods=['GET', 'POST'])
def newItem():
    pass

@app.route('/categories/<int:category_id>/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem():
    pass

@app.route('/categories/<int:category_id>/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem():
    pass

if __name__ == '__main__':
    app.secret_key = '7)o!a(k)wmgv)bxd)x44cvm0v=pc2&pfdwu45&3lrgp!p^+'
    app.debug = True
    app.run(host='0.0.0.0', port = 8000)
