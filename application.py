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

@app.route('/categories/<string:category_name>/edit/', methods=['GET', 'POST'])
def edit_category(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
        session.add(category)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template('edit_category.html', category = category)

@app.route('/categories/<string:category_name>/delete/', methods=['GET', 'POST'])
def delete_category(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template('delete_category.html', category = category)

@app.route('/categories/<string:category_name>/')
def show_items(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = category.id)
    return render_template('categories.html', categories = categories, category = category, items = items)

@app.route('/categories/<string:category_name>/new/', methods=['GET', 'POST'])
def new_item(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        item = Item(name = request.form['name'], category_id = category.id)
        session.add(item)
        session.commit()
        return redirect(url_for('show_items', category_name = category_name))
    else:
        return render_template('new_item.html', category_name = category_name)

@app.route('/categories/<string:category_name>/<string:item_name>/edit/', methods=['GET', 'POST'])
def edit_item(category_name, item_name):
    item = session.query(Item).filter_by(name = item_name).one()
    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        session.add(item)
        session.commit()
        return redirect(url_for('show_items', category_name = category_name))
    else:
        return render_template('edit_item.html', category_name = category_name, item = item)

@app.route('/categories/<string:category_name>/<string:item_name>/delete/', methods=['GET', 'POST'])
def delete_item(category_name, item_name):
    item = session.query(Item).filter_by(name = item_name).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('show_items', category_name = category_name))
    else:
        return render_template('delete_item.html', category_name = category_name, item = item)

if __name__ == '__main__':
    app.secret_key = '7)o!a(k)wmgv)bxd)x44cvm0v=pc2&pfdwu45&3lrgp!p^+'
    app.debug = True
    app.run(host='0.0.0.0', port = 8000)
