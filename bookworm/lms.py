import datetime

from flask import (
    Blueprint, render_template, url_for
)

api = Blueprint('lms', __name__, url_prefix='/lms')
app = Blueprint('app', __name__)

def add_return_message(msg_list, new_msg, msg_type):
    type = 'Success'
    if msg_type == None:
        type = msg_type

    msg_list.append({
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%s %H:%M:%S'),
        'type': type,
        'content': new_msg
    })
    
    
def build_navbar_content():
    sections = {
        'Books': [
            {
                'title': 'Add Books',
                'url': url_for('app.add_books')
            },
            {
                'title': 'Update Books',
                'url': url_for('app.update_books')
            }
        ],
        'Members': [
            {
                'title': 'Add Members',
                'url': url_for('app.add_members')
            },
            {
                'title': 'Update Members',
                'url': url_for('app.update_members')
            }
        ],
        'Transactions': [
            {
                'title': 'Issue Books',
                'url': url_for('app.issue_books')
            },
            {
                'title': 'Return Books',
                'url': url_for('app.return_books')
            },
        ],
        'Reports': [
            {
                'title': 'Most Popular Books',
                'url': url_for('app.popular_books')
            },
            {
                'title': 'Highest Paying Customer',
                'url': url_for('app.paying_customers')
            } ],
        'API': [
            {
                'title': 'Frappe API',
                'url': url_for('app.frappe_api')
            }
            ]

    }

    return sections

@app.route('/index.html', methods=['GET'])
def index():
    content = {'title': "HomePage", 'navbar_sections': build_navbar_content()}
    return render_template('index.html', content = content)

@app.route('/addbooks.html', methods=['GET'])
def add_books():
    content = {'title': "Books - Add", 'navbar_sections': build_navbar_content()}
    return render_template('addbooks.html', content = content)

@app.route('/updatebooks.html', methods=['GET'])
def update_books():
    content = {'title': "Books - Update", 'navbar_sections': build_navbar_content()}
    return render_template('updatebooks.html', content = content)

@app.route('/addmembers.html', methods=['GET'])
def add_members():
    content = {'title': "Members - Add", 'navbar_sections': build_navbar_content()}
    return render_template('addmembers.html', content = content)

@app.route('/updatemembers.html', methods=['GET'])
def update_members():
    content = {'title': "Members - Update", 'navbar_sections': build_navbar_content()}
    return render_template('updatemembers.html', content = content)

@app.route('/issuebooks.html', methods=['GET'])
def issue_books():
    content = {'title': "Issue Books", 'navbar_sections': build_navbar_content()}
    return render_template('issuebooks.html', content = content)

@app.route('/returnbooks.html', methods=['GET'])
def return_books():
    content = {'title': "Return Book", 'navbar_sections': build_navbar_content()}
    return render_template('returnbooks.html', content = content)

@app.route('/popularbook.html', methods=['GET'])
def popular_books():
    content = {'title': "Most Popular Books", 'navbar_sections': build_navbar_content()}
    return render_template('popularbooks.html', content = content)

@app.route('/customers.html', methods=['GET'])
def paying_customers():
    content = {'title': "Highest Paying Customers", 'navbar_sections': build_navbar_content()}
    return render_template('customers.html', content = content)


@app.route('/frappe_api.html', methods=['GET'])
def frappe_api():
    content = {'title': "Frappe API", 'navbar_sections': build_navbar_content()}
    return render_template('frappe_api.html', content = content)
