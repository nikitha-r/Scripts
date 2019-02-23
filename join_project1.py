from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)

db = SQLAlchemy()


class Customer(db.Model):
    """Customer Model."""

    __tablename__ = 'customer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    orders = db.relationship('Purchase', backref='customer')



class Purchase(db.Model):
    """Purchase Model."""

    __tablename__ = 'purchase'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    price = db.Column(db.Integer)


class TestOuterLeftJoinApi(Resource):

	def get(self):
		"""
        The LEFT JOIN keyword returns all records from the left table (table1), and the matched records from the right table (table2).

        SELECT column_name(s)
        FROM table1
        LEFT JOIN table2
        ON table1.column_name = table2.column_name;

        SELECT *
        FROM Customer 
        LEFT JOIN Purchase ON customer.id = Purchase.Customer_id)

        """


		print db.session.query(Customer, Purchase).outerjoin(Purchase, Customer.id == Purchase.customer_id).all()
		print db.session.query(Customer.name, Purchase.name, Purchase.price).outerjoin(Purchase, Customer.id == Purchase.customer_id).all()


		cust = db.session.query(Customer).filter_by(id =1).one()
		print cust.orders[0].name
		print cust.orders[0].customer_id, cust.orders[0].name, cust.orders[0].price


		"""
		Error: InvalidRequestError: Can't join table/selectable 'purchase' to itself.
			This is where we need left join.
		"""
		# print db.session.query(Purchase, Customer).join(Purchase, Purchase.customer_id == Customer.id).all()
		# print db.session.query(Purchase, Customer).join(Purchase).filter(Purchase.customer_id == Customer.id).all()


class TestOuterRightJoinApi(Resource):

	def get(self):
		pass


api.add_resource(
    TestOuterLeftJoinApi, '/leftjoin')

api.add_resource(
    TestOuterRightJoinApi, '/rightjoin')




if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/join_project1'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    app.run(debug=True)



############TABLE##############
Customer        Purchase

id name         id name   customer_id price
1  Cust1        1  Tshirt 1           200
2  Cust2        2  Jeans  1           1000
                3	 Tshirt	2	          100
                4	 Jeans	2	          500
                5	 Top	  1	          100


