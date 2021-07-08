from datetime import datetime

from flask import(
    Blueprint, request, current_app, jsonify
)

from bookworm.lms import api
from bookworm.lms import add_return_message
from bookworm.db_orm import *

def build_shallow_book_dict(book):
    bk_dict = book.dict()
    del bk_dict['isbn13']
    del bk_dict['publication_date']
    del bk_dict['publisher']
    return bk_dict

def get_books():
    session = current_app.config['DB_SESSIONMAKER']()
    books = session.query(Book).all()
    bks = [build_shallow_book_dict(x) for x in books]
    session.close()
    return bks

def build_shallow_member_dict(member):
    mem_dict = member.dict()
    del mem_dict['created_on']
    del mem_dict['emailid']
    return mem_dict

def get_members():
    session = current_app.config['DB_SESSIONMAKER']()
    members = session.query(Member).all()
    members = [build_shallow_member_dict(x) for x in members]
    session.close()
    return members

def build_issueform_data():
    members = get_members()
    bks = get_books()
    ret_msg = { 'books': bks, 'members': members }
    return ret_msg

@api.route('/get_issueform_data', methods=['GET'])
def get_issueform_data():
    return jsonify(build_issueform_data())

@api.route('/getIssued', methods=['GET'])
def get_issued_books():
    session = current_app.config['DB_SESSIONMAKER']()
    return_obj = []
    active_transactions = session.query(BookIssue).filter(BookIssue.active == True)
    for transaction in active_transactions:
        return_obj.append(
            { 'transactionid': transaction.transactionid,
              'member': transaction.member.dict(),
              'book': transaction.book.dict(),
              'paid': transaction.charge.paid,
              'issued_date': transaction.issued_date.strftime('%Y-%m-%d'),
              'returned_date': '' if transaction.returned_date == None else transaction.returned_date.strftime('%Y-%m-%d')
             })
    session.close()
    return jsonify(return_obj)

@api.route('/getUnpaid', methods=['GET'])
def get_unpaid_returns():
    session = current_app.config['DB_SESSIONMAKER']()
    return_obj = []
    unpaid_transactions = session.query(BookIssue).filter(BookIssue.active==False)
    for transaction in unpaid_transactions:
        if not transaction.charge.paid:
            return_obj.append(
                { 'transactionid': transaction.transactionid,
                  'member': transaction.member.dict(),
                  'book': transaction.book.dict(),
                  'issued_date': transaction.issued_date.strftime('%Y-%m-%d'),
                  'returned_date': None if transaction.returned_date == None else transaction.returned_date.strftime("%Y-%m-%d"),
                  'rent_fee': transaction.charge.amountdue,
                 })
    session.close()
    return jsonify(return_obj)

def book_issue_logic(member, book):
    logic_decision = { 'can_borrow': False ,'err_msgs':[] }
    max_debt = 500
    max_borrow = 5
    
    # book in stock
    have_stock = False
    # check if stock is available
    if book.stock.available_quantity > 0:
        have_stock = True
    else:
        logic_decision['err_msgs'].append("Book not in stock")
                    
    # outstanding < 500
    has_debt = False
    user_debt = 0
    for x in member.returned_books:
        if not x.charge.paid:
            user_debt += x.charge.amountdue

    for x in member.holding_books:
        fine = 0
        duration = datetime.date.today() - x.issued_date
        days_after_borrow_limit = duration.days - 30
        if days_after_borrow_limit > 0:
            fine = 100 if days_after_borrow_limit * 1 > 100 else days_after_borrow_limit * 1
            user_debt += fine

    if user_debt >= 400:
        has_debt = True
        logic_decision['err_msgs'].append("Member has reached maximum outstanding debt.")
    else:
        has_debt = False
    
    # Borrow limit
    borrow_limit_reached = True
    borrow_power = (max_debt - user_debt) / 500
    borrow_limit =int(borrow_power * max_borrow) if (int(borrow_power * max_borrow) < (max_borrow - len(member.holding_books))) else (max_borrow - len(member.holding_books))
    # if (len(member.holding_books) >= borrow_limit):
    if borrow_limit == 0:
        logic_decision['err_msgs'].append("Member has reached borrow limit.")
    else:
        borrow_limit_reached = False

    # multiple copies not allowed
    # check if the user has already taken a copy of the book
    has_a_copy = False
    for currently_holding in member.holding_books:
        if currently_holding.bookid == book.bookid:
            has_a_copy = True
            break
    if has_a_copy:
        logic_decision['err_msgs'].append("Member has already borrowed this book")

    if have_stock and not has_debt and not borrow_limit_reached and not has_a_copy:
        logic_decision['can_borrow']= True

    return logic_decision


@api.route('/issuebook', methods=['POST'])
def issue_book():
    if request.is_json:
        try:

            return_msg = { 'message': [] }
            content = request.get_json()
            session = current_app.config['DB_SESSIONMAKER']()
            if 'selected_book' in content.keys() and 'selected_member' in content.keys():
                sel_book = session.query(Book).filter(Book.bookid == content['selected_book']['bookid']).first()
                sel_member = session.query(Member).filter(Member.memberid == content['selected_member']['memberid']).first()

                decision = book_issue_logic(sel_member, sel_book)
                if decision['can_borrow']:
                    issue = BookIssue()
                    issue.bookid = sel_book.bookid
                    issue.memberid = sel_member.memberid
                    issue.created_on = datetime.date.today()
                    if 'issueDate' in content.keys():
                        issue.issued_date = datetime.datetime.strptime(content['issueDate'], '%Y-%m-%d')
                    else:
                        issue.issued_date = datetime.date.today()

                    # initialize rent
                    rent = Debt()
                    rent.amountdue = 0
                    issue.charge = rent
                    # update stock
                    sel_book.stock.available_quantity -= 1

                    session.add(issue)
                    session.add(sel_book)
                    try:
                        session.commit()
                        add_return_message(return_msg['message'], 'Book has been issued', 'Success')
                    except Exception as commit_exception:
                        add_return_message(return_msg['message'], commit_exception.args, 'Error')
                        session.rollback()
                else:
                    for x in decision['err_msgs']:
                        add_return_message(return_msg['message'], x, 'Error')
            else:
                add_return_message(return_msg['message'], 'Cirtical parameters missing', 'Error')
            session.close()
        except Exception as unknown_exception:
            add_return_message(return_msg['message'], unknown_exception.args, 'Error')

        ret_form_data = build_issueform_data()
        return_msg['books'] = ret_form_data['books']
        return_msg['members'] = ret_form_data['members']
            
    return jsonify(return_msg);


@api.route('/issuereturn', methods=['POST'])
def issue_return():
    if request.is_json:
        try:

            return_msg = { 'message': []}
            content = request.get_json()
            session = current_app.config['DB_SESSIONMAKER']()
            bookids = []
            memberids = []
            dates = []
            transaction_ids = []
            
            if 'returned_books' in content.keys():
                if not content['returned_books'] == []:
                    for x in content['returned_books']:
                        transaction_ids.append(x['transactionid'])

                        issued_books = session.query(BookIssue).filter(BookIssue.transactionid.in_(transaction_ids))

                    # update return date
                    for transaction in issued_books:
                        ret_book = None
                        for book in content['returned_books']:
                            if book['transactionid'] == transaction.transactionid:
                                ret_book = book
                                break;
                            
                        if ret_book != None:
                            if 'returned_date' in ret_book.keys():
                                transaction.returned_date = datetime.datetime.strptime(ret_book['returned_date'],"%Y-%m-%d").date()
                                transaction.active = False

                                # Update stock
                                transaction.book.stock.available_quantity += 1

                                # Charge rent
                                delta = transaction.returned_date - transaction.issued_date
                                rent_fee = 0 if delta.days <= 30 else (delta.days - 30) * 1
                                rent_fee = 100 if (rent_fee/100) >= 1 else (rent_fee%100)
                                transaction.charge.amountdue = rent_fee
                                
                                if 'paid' in ret_book.keys():
                                    transaction.charge.paid = ret_book['paid']

                                session.add(transaction)
                            else:
                                add_return_message(return_msg['message'], "Bookid:%d, Memberid: %d is missing returned date" % (ret_book['bookid'] ,ret_book['memberid']), 'Error')
                        
                    try:
                        session.commit()
                        add_return_message(return_msg['message'], 'Book returned', 'Success')
                    except Exception as commit_exception:
                        add_return_message(return_msg['message'], commit_exception.args, 'Error')
                        session.rollback()
                else:
                    add_return_message(return_msg['message'], 'No books were selected', 'Error')
                    session.close()
            else:
                add_return_message(return_msg['message'], 'Cirtical parameters missing', 'Error')
            session.close()
        except Exception as unknown_exception:
            add_return_message(return_msg['message'], unknown_exception.args, 'Error')

        ret_form_data = build_issueform_data()
        return_msg['books'] = ret_form_data['books']
        return_msg['members'] = ret_form_data['members']
            
    return jsonify(return_msg);


@api.route('/payDebt', methods=['POST'])
def get_transaction_debt():
    if request.is_json:
        try:

            return_msg = { 'message': []}
            content = request.get_json()
            session = current_app.config['DB_SESSIONMAKER']()
            transaction_ids = []
            
            if 'paid_books' in content.keys():
                if not content['paid_books'] == []:
                    for x in content['paid_books']:
                        transaction_ids.append(x['transactionid'])

                        unpaid_transactions = session.query(BookIssue).filter(BookIssue.transactionid.in_(transaction_ids))

                    # update paid flag
                    for transaction in unpaid_transactions:
                        tran = None
                        for x in content['paid_books']:
                            if x['transactionid'] == transaction.transactionid:
                                tran = x
                                break;
                            
                        if tran != None:
                            if 'paid' in tran.keys():
                                transaction.charge.paid = True
                            else:
                                transaction.charge.paid = False

                                session.add(transaction)

                    try:
                        session.commit()
                        add_return_message(return_msg['message'], 'Debt Paid', 'Success')
                    except Exception as commit_exception:
                        add_return_message(return_msg['message'], commit_exception.args, 'Error')
                        session.rollback()
                else:
                    add_return_message(return_msg['message'], 'No transactions were selected', 'Error')
                    session.close()
            else:
                add_return_message(return_msg['message'], 'Cirtical parameters missing', 'Error')
            session.close()
        except Exception as unknown_exception:
            add_return_message(return_msg['message'], unknown_exception.args, 'Error')

        ret_form_data = build_issueform_data()
        return_msg['books'] = ret_form_data['books']
        return_msg['members'] = ret_form_data['members']
            
    return jsonify(return_msg);
