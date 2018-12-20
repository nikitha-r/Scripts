"""
The possible exceptions for api requests
"""
class ApiException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class RecordNotFoundException(ApiException):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


errors = {
    'RecordNotFoundException': {
       'message': 'Record not found in the Database.',
       'status': 404
    }
}

"""API View to raise customized exception"""
def get(self, run_key):
    try:
        demo_obj = DemoModel.query.filter_by(some_field=1).one()
        return demo_obj
    except NoResultFound, e:
        logging.info("No record found")
        raise RecordNotFoundException()
