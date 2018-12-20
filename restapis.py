from app.models.models import DemoModel
from flask import jsonify

class DemoApi(Resource):
    """API implementation to fetch the record of id without any packages."""

    def get(self, id):
        """Handle 'GET'request."""
        try:
            demo_obj = DemoModel.query.get(id)
            if demo_obj is not None:
                demo_res_dict = {}
                res_dict = demo_obj.__dict__
                res_dict.pop('_sa_instance_state')
                for key,value in res_dict.iteritems():
                    if (type(value) == decimal.Decimal):
                        value = float(value)
                    demo_res_dict[key] = value
                return jsonify(demo_res_dict)
            else:
                logging.info('Given id does not exist.')
                return {'GET': "Given id does not exist."}
        except Exception, e:
            logging.info(e)
            raise e

            
class SetApi(Resource):
    """API implementation to set."""

    def put(self, id):
        try:
            demo_record = DemoModel.query.get(id)
            if demo_record is not None:
                demo_record.age = 18
                db.session.commit()
                demo_record_dict = {}
                res_dict = demo_record.__dict__
                res_dict.pop('_sa_instance_state')
                for key,value in res_dict.iteritems():
                    if (type(value) == decimal.Decimal):
                        value = float(value)
                    demo_record_dict[key] = value
                return jsonify(demo_record_dict)
            else:
                logging.info('Given  id does not exist.')
                return {'PUT': 'Given  id does not exist.'}
        except Exception, e:
            logging.info('Failed to set the age. ')
            raise e

            
 class CreateApi(Resource):
    """API implementation to ingest the record."""

    def get(self):
        return {'GET': "Api"}

    def post(self):
        """Handle 'POST'request """
        try:
            json_result = request.get_json(force=True)
            jsonified_msg = create_record(json_result)
            return jsonified_msg
        except Exception, e:
            logging.info('Failed to create the record.')
            raise e
