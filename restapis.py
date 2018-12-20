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
