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
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('categories.html', categories = categories)

@app.route('/categories/new/', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name = request.form['name'])
        session.add(newCategory)
        session.commit()
        flash('New category created!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcategory.html')

if __name__ == '__main__':
    app.secret_key = '7)o!a(k)wmgv)bxd)x44cvm0v=pc2&pfdwu45&3lrgp!p^+'
    app.debug = True
    app.run(host='0.0.0.0', port = 8000)
