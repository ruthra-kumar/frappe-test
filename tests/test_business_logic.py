import os
import tempfile
import unittest
import flask
from bookworm import create_app

class test_LibERP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app_instance = create_app({
            'TESTING': True
        })
        cls.app_instance = app_instance
        cls.app = app_instance.test_client()

    def test_01_hello(self):
        response = self.app.get("/hello.json")
        return_data = flask.json.loads(response.get_data())
        self.assertEqual(return_data['greetings'], "Hello World")

    def test_02_addbooks(self):
        with open("tests/books.json") as data:
            response = self.app.post('/lms/addbooks',json={
                'newbooks': flask.json.loads(data.read())
            })
            return_data = flask.json.loads(response.get_data())
            self.assertEqual(return_data['message'][0]['content'],'Books Added')

    def test_03_addmembers(self):
        with open("tests/members.json") as data:
            response = self.app.post('/lms/addmembers', json={
                'newmembers': flask.json.loads(data.read())
            })
            return_data =  flask.json.loads(response.get_data())
            self.assertEqual(return_data['message'][0]['content'],"Members Added")

    def test_04_bookissue(self):
        with open("tests/issuebook.json") as data:
            book_issues = flask.json.loads(data.read())

        responses = []
        for x in book_issues:
            responses.append(self.app.post('/lms/issuebook', json={'selected_book':x['selected_book'], 'issueDate': x['issueDate'], 'selected_member': x['selected_member']}))            

        for response in responses:
            with self.subTest():
                messages=flask.json.loads(response.get_data())['message']
                self.assertIn("Book has been issued",messages[0]['content'])

    def test_05_bookreturn(self):
        transactions = flask.json.loads(self.app.get('/lms/getIssued').get_data())
        responses = []
        for x in transactions:
            responses.append(self.app.post('/lms/issuereturn', json={'returned_books':[{ 'transactionid': x['transactionid'], 'returned_date': '2021-06-09' }]}))

        for response in responses:
            with self.subTest():
                messages=flask.json.loads(response.get_data())['message']
                self.assertIn("Book returned",messages[0]['content'])

    def test_06_issuelogic(self):
        with open("tests/issuebook.json") as data:
            book_issues = flask.json.loads(data.read())

        responses = []
        x = book_issues[0]
        responses.append(self.app.post('/lms/issuebook', json={'selected_book':x['selected_book'], 'issueDate': x['issueDate'], 'selected_member': x['selected_member']}))            

        self.assertIn("Member has reached maximum outstanding debt.",flask.json.loads(responses[0].get_data())['message'][0]['content'])
     
    def test_07_paydebt(self):
        unpaid_transactions = flask.json.loads(self.app.get('/lms/getUnpaid').get_data())
        transaction = unpaid_transactions[0]
        response = self.app.post('/lms/payDebt',json={'paid_books':[{'transactionid': transaction['transactionid'], 'paid':'on'}]})
        self.assertIn("Debt Paid",flask.json.loads(response.get_data())['message'][0]['content'])
        
    # @classmethod
    # def tearDownClass(cls):
    #     os.remove(cls.app_instance.config['DATABASE'])


if __name__ == "__main__":
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    suite.addTests(loader.loadTestsFromTestCase(test_LibERP))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)

