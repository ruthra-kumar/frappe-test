import os
import pprint

from flask import (
    Blueprint, render_template, request, flash, current_app, jsonify
)

from bookworm.lms import api
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
            
            if 'newmembers' in content.keys():
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
                    return_msg['message'].append('Members Added')
                    current_app.logger.info('Members Added')
                except Exception as e:
                    session.rollback()
                    return_msg['message'].append(e.args)
                    current_app.logger.error(e.args)
            else:
                return_msg['message'].append('New Members data missing')
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
                    del_members = session.query(Member).filter(Member.memberid.in_(memberids))
                    list(map(lambda mem: session.delete(mem), del_members))
                    try:
                        session.commit()
                        return_msg['message'].append('Members Deleted')
                    except Exception as commit_exception:
                        current_app.logger.debug(commit_exception.args)
                        return_msg['message'].append( commit_exception.arg )
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
                        return_msg['message'].append('Members Updated')
                    except Exception as commit_exception:
                        current_app.logger.debug(commit_exception.args)
                        return_msg['message'].append(commit_exception.args)
                        session.rollback()

        except Exception as unknown:
            current_app.logger.debug(type(unknown),unknown.args)
            return_msg['message'].append(unknown.args)
            
        session.close()
        return jsonify(return_msg)
                    
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

    session.close()
    return jsonify({'customers': customers[0:3]})
