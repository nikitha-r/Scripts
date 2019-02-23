from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)

db = SQLAlchemy()



class Physiology(db.Model):
    """League Model."""

    __tablename__ = 'physiology'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name, abbreviation, other_names):
        self.name = name


class Lifestyle(db.Model):
    """Round Model."""

    __tablename__ = 'lifestyle'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    physiology_id = db.Column(db.Integer, db.ForeignKey('physiology.id'))

    physiology = db.relationship('Physiology', backref='physiology')


class Simulation(db.Model):
    """Game model."""

    __tablename__ = "simulation"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    lifestyle_id = db.Column(db.Integer, db.ForeignKey('lifestyle.id'))

    lifestyle = db.relationship('Lifestyle', backref="lifestyle")


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
        print db.session.query(Physiology, Lifestyle).outerjoin(Lifestyle, Physiology.id == Lifestyle.physiology_id).all()
        print db.session.query(Physiology.name, Lifestyle.name, Lifestyle.physiology_id).outerjoin(Lifestyle, Physiology.id == Lifestyle.physiology_id).all()




class TestInnerJoinApi(Resource):

    def get(self):
        """INNER JOINS: Returns records that have matching values in both tables
        Querying with joins with three tables. 

        SELECT column_name(s)
        FROM table1
        INNER JOIN table2
        ON table1.column_name = table2.column_name;

        SELECT Orders.OrderID, Customers.CustomerName, Shippers.ShipperName
        FROM ((Orders
        INNER JOIN Customers ON Orders.CustomerID = Customers.CustomerID)
        INNER JOIN Shippers ON Orders.ShipperID = Shippers.ShipperID);



        SELECT Simulation.name, Lifestyle.name
        FROM Lifestyle
        INNER JOIN Physiology ON Lifestyle.physiology_id=Physiology.id;

        with_entities: Use to retrieve specific fields.
        without with_entities: Use to retrieve the objects Simulation.
        """
        sim_lif_phys_three_query = Simulation.query.with_entities(Simulation.name, Lifestyle.name).join(Lifestyle).join(Physiology, Lifestyle.physiology_id == Physiology.id).all()
        sim_lif_phys_three = Simulation.query.join(Lifestyle).join(Physiology).filter(Lifestyle.physiology_id == Physiology.id).all()


        """Querying with joins with two tables. """
        sim_lif_phys_two = Lifestyle.query.with_entities(Lifestyle.name).join(Physiology, Lifestyle.physiology_id == Physiology.id).all()

        print sim_lif_phys_two






class TestBacRefApi(Resource):

    def get(self):
        lifestyle_obj_list = []
        result = db.session.query(Simulation).filter(Simulation.lifestyle_id.in_([1,2])).all()

        simulation_obj = db.session.query(Simulation).filter_by(lifestyle_id=1).first()
        print "simulation_obj", simulation_obj
        print "lifestyle_obj", simulation_obj.lifestyle
        print "physiology_obj", simulation_obj.lifestyle.physiology


        simulation_objs = db.session.query(Simulation).filter_by(lifestyle_id=1).all()
        print "simulation_objs", simulation_objs
        print "lifestyle_objs"
        for lifestyle_obj in simulation_objs:
            print lifestyle_obj.lifestyle
            lifestyle_obj_list.append(lifestyle_obj.lifestyle)

        print "physiology_objs"
        for lifestyle_obj in lifestyle_obj_list:
            print lifestyle_obj.physiology

api.add_resource(
    TestInnerJoinApi, '/innerjoin')
api.add_resource(
    TestBacRefApi, '/backref')
api.add_resource(
    TestOuterLeftJoinApi, '/outerleftjoin')


if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/join_project'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    app.run(debug=True)


#######TABLE##########

Physiology            Lifestyle                           Simulation

id name               id name    physiokogy_id            id name    lifestyle_id
1  Pname              1  Lname1  1                        1  Sname1  1
                      2  Lname2  2                        2  Sname2  1
