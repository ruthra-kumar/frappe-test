import os
import pprint
from datetime import datetime

from flask import (
    Blueprint, render_template, request, flash, current_app, jsonify
)

from bookworm.lms import api
from bookworm.db_orm import *

@api.route('/listbooks', methods=['GET'])    
def list_books():
    session = current_app.config['DB_SESSIONMAKER']()
    allbooks = session.query(Book).all()
    bks = [x.dict() for x in allbooks]
    session.close()
    return jsonify(bks)
    
@api.route('/addbooks', methods=['POST'])
def addbooks():
    if request.is_json:
        try:
            session = current_app.config['DB_SESSIONMAKER']()
            content = request.get_json()
            return_msg  ={ 'message': ''}

            if 'newbooks' in content.keys():
                for x in content['newbooks']:
                    bk = Book()
                    if x['bookid']:
                        bk.bookid = x['bookid']
                    bk.title = x['title']
                    bk.authors = x['authors']
                    bk.isbn13 = x['isbn13']
                    bk.publication_date = datetime.datetime.strptime(x['publication_date'], "%Y-%m-%d")
                    bk.publisher = x['publisher']
                    sk = Stock()
                    sk.available_quantity = x['quantity']
                    sk.total_quantity = x['quantity']
                    bk.stock = sk

                    session.add(bk)
                    session.add(sk)

                try:
                    session.commit()
                    current_app.logger.debug('Books added')
                    return_msg['message'] = 'Books Added'
                except Exception as commit_exception:
                    current_app.logger.debug(commit_exception.args)
                    return_msg['message'] = commit_exception.args
                    session.rollback()
        except Exception as unknown:

            current_app.logger.debug(type(unknown),unknown.args)
            return_msg['message'] = unknown.args

        session.close()
        return jsonify(return_msg)

def search_books(item, itm_list):
    for x in itm_list:
        if x['bookid'] == item.bookid:
            return x
    return None

@api.route('/updatebooks', methods=['POST'])
def updatebooks():
    if request.is_json:

        try:
            session = current_app.config['DB_SESSIONMAKER']()
            content = request.get_json()
            return_msg  ={ 'message': []}

            if 'deleted_books' in content.keys():
                bookids = []
                list(map(lambda x: bookids.append(x['bookid']), content['deleted_books']))

                if bookids:
                    del_books = session.query(Book).filter(Book.bookid.in_(bookids))
                    
                    # If any book marked for deletion has active holders, don't delete
                    has_holders = False
                    for x in del_books:
                        if len(x.active_holders) > 0:
                            return_msg['message'].append('{} has holders'.format(x.bookid))
                            has_holders = True


                    if not has_holders:
                        list(map(lambda book: session.delete(book), del_books))
                        try:
                            session.commit()
                            return_msg['message'].append('Books Deleted')
                        except Exception as commit_exception:
                            current_app.logger.debug(commit_exception.args)
                            return_msg['message'].append( commit_exception.arg )
                            session.rollback()

            if 'modified_books' in content.keys():
                bookids = []

                list(map(lambda x: bookids.append(x['bookid']), content['modified_books']))

                if bookids:
                    edited_books = session.query(Book).filter(Book.bookid.in_(bookids))

                    for book in edited_books:
                        updated_book = search_books(book, content['modified_books'])
                        if updated_book:
                            # Make sure that new quantity is not lower that no of books issued
                            in_use = book.stock.total_quantity - book.stock.available_quantity
                            new_quantity = int(updated_book['quantity'])
                            if new_quantity >= in_use:
                                if book.stock.total_quantity >= new_quantity:
                                    book.stock.total_quantity -= book.stock.total_quantity - new_quantity
                                    book.stock.available_quantity = book.stock.total_quantity - in_use
                                else:
                                    book.stock.total_quantity = new_quantity
                                    book.stock.available_quantity = book.stock.total_quantity - in_use
                            else:
                                return_msg['message'].append('Bookid: {} - Quantity cannot be lower than {}'.format(book.bookid, in_use))
                                break

                            book.title = updated_book['title']
                            book.authors = updated_book['authors']
                            book.isbn13 = updated_book['isbn13']
                            book.publication_date = datetime.datetime.strptime(updated_book['publication_date'], "%Y-%m-%d")
                            book.publisher = updated_book['publisher']

                                
                                
                            # book.stock.available_quantity = updated_book['quantity']
                            # book.stock.total_quantity = updated_book['quantity']

                            session.add(book)
                            session.add(book.stock)
                        
                            try:
                                session.commit()
                                current_app.logger.debug('Books Updated')
                                return_msg['message'].append('Books Updated')
                            except Exception as commit_exception:
                                current_app.logger.debug(commit_exception.args)
                                return_msg['message'].append(commit_exception.args)
                                session.rollback()
        except Exception as unknown:
            current_app.logger.debug(type(unknown),unknown.args)
            return_msg['message'].append(unknown.args)
            
        session.close()
        return jsonify(return_msg)
    
@api.route('/popularbooks', methods=['GET'])
def get_popular_books():
    session = current_app.config['DB_SESSIONMAKER']()
    ret_data =  {
        'books':[],
        'message':[]
    }
    all_books = session.query(Book).all()

    all_books.sort(key=lambda book:len(book.holders), reverse=True)
    for x in all_books:
        ret_data['books'].append({
            'bookid': x.bookid,
            'title': x.title,
            'authors': x.authors,
            'available_quantity': x.stock.available_quantity,
            'total_quantity': x.stock.total_quantity,
            'holders': len(x.holders)
            })

    session.close()
    ret_data['books'] = ret_data['books'][0:5]
    return jsonify(ret_data)
