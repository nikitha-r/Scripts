*******************API*******************
from flask import request
class BarApi(MethodResource):
    def get(self):
        print request.args 
        
*******************Testcase*******************
from calibration_service_app import db, app
from calibration_service_app.tests.base import BaseTest


class TestBar(BaseTest):

    @classmethod
    def setUpClass(cls):
        """Setup method to handle test setup."""
        super(TestBar, cls).setUpClass()

        # Create test client
        db.create_all()
        app.testing = True
        cls.app = app.test_client()

    def test_api(self):
        res = self.app.get(
            '/bar?key1=val1&key2=val2')
        self.assertEqual(res.status_code, 200)

