import requests

from flask import (
    current_app, request
)

from bookworm.lms import api

@api.route('/proxy_frappe_api', methods=['GET'])
def proxy_frappe_api():
    response = requests.get('https://frappe.io/api/method/frappe-library',
                            params={
                                'title': request.args['title'],
                                'author': request.args['author'],
                                'isbn': request.args['isbn'],
                                'publisher': request.args['publisher'],
                                'page': request.args['page'],
                            })
    return response.content






