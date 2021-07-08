import os
import pprint

from flask import (
    Blueprint, render_template, request, flash, current_app, jsonify
)

from bookworm.lms import api
from bookworm.lms import add_return_message
from bookworm.db_orm import *

@api.route('/listmembers', methods=['GET'])    
def list_members():
    session = current_app.config['DB_SESSIONMAKER']()
    allmembers = session.query(Member).all()
    mems = [x.dict() for x in allmembers]
    session.close()
    return jsonify(mems)

@api.route('/addmembers', methods=['POST'])
def addmembers():
    if request.is_json:
        try:
            session = current_app.config['DB_SESSIONMAKER']()
            ret = None
            content = request.get_json()
            return_msg = { 'message': [] }

            # Check if members are there in database           
            if 'newmembers' in content.keys():
                memberids = []
                for x in content['newmembers']:
                    memberids.append(x['memberid'])

                members_found = session.query(Member).filter(Member.memberid.in_(memberids))
                if members_found.all() != []:
                    for x in members_found:
                        add_return_message(return_msg['message'], 'Member {} already exists'.format(x.memberid), 'Error')
                else:

                    # Add new members to DB
                    for x in content['newmembers']:
                        mem = Member()
                        mem.memberid = x['memberid']
                        mem.first_name = x['first_name']
                        mem.last_name = x['last_name']
                        mem.emailid = x['emailid']
                        mem.created_on = datetime.datetime.strptime(x['created_on'], "%Y-%m-%d")
                        session.add(mem)

                        try:
                            session.commit()
                            add_return_message(return_msg['message'], 'Members Added', 'Success')
                            # current_app.logger.info('Members Added')
                        except Exception as e:
                            session.rollback()
                            add_return_message(return_msg['message'], e.args, 'Error')
                            current_app.logger.error(e.args)
            else:
                add_return_message(return_msg['message'], 'New Members data missing', 'Error')
                current_app.logger.debug('New Members data missing')

        # Payload issues
        except Exception as unknown_exc:
            ret = unknown_exc.args
            current_app.logger.error(unknown_exc.args)            

        return jsonify(return_msg)

def search_members(item, itm_list):
    for x in itm_list:
        if x['memberid'] == item.memberid:
            return x
    return None

@api.route('/updatemembers', methods=['POST'])
def updatemembers():
    if request.is_json:
        try:
            session = current_app.config['DB_SESSIONMAKER']()
            content = request.get_json()
            return_msg  ={ 'message': []}

            if 'deleted_members' in content.keys():
                memberids = []
                list(map(lambda x: memberids.append(x['memberid']), content['deleted_members']))

                if memberids:
                    perform_deletion = True
                    del_members = session.query(Member).filter(Member.memberid.in_(memberids))
                    
                    # make sure member has no active book holdings and outstanding debt
                    for x in del_members:
                        if x.holding_books != []:
                            add_return_message(return_msg['message'], 'Member: {}  has unreturned books.'.format(x.memberid), 'Error')
                            return_msg['deletion_opr'] = 'Error'
                            perform_deletion = False

                        if x.dict()['outstanding_debt'] > 0:
                            add_return_message(return_msg['message'], 'Member: {}  has Outstanding Debt.'.format(x.memberid), 'Error')
                            return_msg['deletion_opr'] = 'Error'
                            perform_deletion = False
                    
                    
                    if perform_deletion:
                        list(map(lambda mem: session.delete(mem), del_members))
                        try:
                            session.commit()
                            add_return_message(return_msg['message'], 'Members Deleted', 'Success')
                            return_msg['deletion_opr'] = 'Success'
                        except Exception as commit_exception:
                            current_app.logger.debug(commit_exception.args)
                            add_return_message(return_msg['message'],  commit_exception.arg , 'Error')
                            return_msg['deletion_opr'] = 'Success'
                            session.rollback()

            if 'modified_members' in content.keys():
                memberids = []

                list(map(lambda x: memberids.append(x['memberid']), content['modified_members']))
                if memberids:
                    edited_members = session.query(Member).filter(Member.memberid.in_(memberids))
                    for mem in edited_members:
                        updated_member = search_members(mem, content['modified_members'])
                        if updated_member:
                            mem.first_name = updated_member['first_name']
                            mem.last_name = updated_member['last_name']
                            mem.emailid = updated_member['emailid']
                            mem.created_on = datetime.datetime.strptime(updated_member['created_on'], "%Y-%m-%d")
                            session.add(mem)
                        
                    try:
                        session.commit()
                        current_app.logger.debug('Members Updated')
                        add_return_message(return_msg['message'], 'Members Updated', 'Success')
                        return_msg['update_opr'] = 'Success'
                    except Exception as commit_exception:
                        current_app.logger.debug(commit_exception.args)
                        add_return_message(return_msg['message'], commit_exception.args, 'Error')
                        return_msg['update_opr'] = 'Error'
                        session.rollback()

        except Exception as unknown:
            current_app.logger.debug(type(unknown),unknown.args)
            add_return_message(return_msg['message'], unknown.args, 'Error')
            
        session.close()
        return jsonify(return_msg)
                    
# Get top 3 highest paying customers
@api.route('/getCustomers', methods=['GET'])    
def get_customers():
    session = current_app.config['DB_SESSIONMAKER']()
    allmembers = session.query(Member).all()
    customers = []
    for x in allmembers:
        total_amount_paid = 0
        for book in x.books:
            if book.charge.paid:
                total_amount_paid += book.charge.amountdue

        customers.append({
            'memberid': x.memberid,
            'first_name': x.first_name,
            'last_name': x.last_name,
            'paid': total_amount_paid
        })
    customers.sort(key=lambda member: member['paid'], reverse=True)
    session.close()
    return jsonify({'customers': customers[0:3]})
