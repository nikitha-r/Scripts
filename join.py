from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@/degree'

app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)


class UserModel(db.Model):
    """"""
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    degree_id = db.Column(
        db.Integer, db.ForeignKey(
            'Degree.degree_id'), nullable=False)


class DegreeModel(db.Model):
    """"""
    __tablename__ = 'Degree'
    degree_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)



@app.route('/')
def show_all():
    degree_id=[1]
    users_with_same_degree = UserModel.query.join(DegreeModel).filter(
    	UserModel.degree_id == degree_id).all()
    return render_template("show_all.html", users=users_with_same_degree)


if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)
