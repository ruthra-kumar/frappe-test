import datetime
import sqlalchemy
import click
import flask

from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy import create_engine, Column, Integer, BigInteger, DateTime, String, Sequence, Date, Float, Boolean, ForeignKey, Table, exc
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, backref
from sqlalchemy.pool import StaticPool
from functools import reduce

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'

    bookid =  Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    authors = Column(String(300))
    isbn13 = Column(String(13))
    publication_date = Column(Date, default=datetime.date.today())
    publisher = Column(String(200))

    holders = relationship("BookIssue", primaryjoin="BookIssue.bookid == Book.bookid", backref="book", overlaps="past_holders, book, active_holders, book")
    active_holders = relationship("BookIssue",primaryjoin="and_(BookIssue.bookid == Book.bookid, BookIssue.active==True)",  overlaps="past_holders, book, holders, book")
    past_holders = relationship("BookIssue",primaryjoin="and_(BookIssue.bookid == Book.bookid, BookIssue.active==False)", overlaps="active_holders, book, holders, book")

    stock = relationship("Stock",uselist=False, back_populates="book", cascade="all, delete")

    def __repr__(self):
        return "<Book(bookid='%d', title='%s', authors='%s', isbn13='%s', publication_date='%s', publisher='%s')>" % (self.bookid, self.title, self.authors, self.isbn13, self.publication_date, self.publisher)

    def dict(self):
        return { 'bookid':self.bookid, 'title':self.title , 'authors':self.authors, 'isbn13':self.isbn13, 'publication_date':self.publication_date.strftime("%Y-%m-%d"), 'publisher':self.publisher, 'quantity': self.stock.available_quantity}


class Stock(Base):
    __tablename__ = 'stock'
    
    bookid = Column(Integer, ForeignKey('books.bookid'),primary_key=True)
    available_quantity = Column(Integer, nullable=False)
    total_quantity =  Column(Integer, nullable=False)

    book = relationship("Book", back_populates="stock")

    def __repr__(self):
        return "<Stock(bookid='%d', available_quantity='%d', total_quantity='%d')>" % (self.bookid, self.available_quantity, self.total_quantity)

class Member(Base):
    __tablename__ = 'members'
    
    memberid = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    emailid = Column(String(100))
    created_on = Column(Date, default=datetime.date.today())

    books = relationship("BookIssue", primaryjoin="Member.memberid==BookIssue.memberid",backref="member", overlaps="holding_books, member, returned_books, member")
    returned_books = relationship("BookIssue", primaryjoin="and_(Member.memberid==BookIssue.memberid, BookIssue.active==False)", overlaps="holding_books, member, books, member")
    holding_books = relationship("BookIssue", primaryjoin="and_(Member.memberid==BookIssue.memberid, BookIssue.active==True)", overlaps="returned_books, member, books, member")
    
    def __repr__(self):
        return "<Member(memberid='%d', first_name='%s', last_name='%s', emailid='%s', created_on='%s')>" % (self.memberid, self.first_name, self.last_name, self.emailid, self.created_on.strftime("%Y-%m-%d"))


    def dict(self):
        # Calculate outstanding debt
        outstanding_debt = 0
        if self.books == []:
            outstanding_debt = 0
        else:
            outstanding_debt = reduce(lambda x,y: x+y, [x.charge.amountdue * (not x.charge.paid) for x in self.books])

        return { 'memberid':self.memberid, 'first_name':self.first_name , 'last_name':self.last_name, 'emailid':self.emailid, 'created_on':self.created_on.strftime("%Y-%m-%d"), 'outstanding_debt': outstanding_debt}

class Debt(Base):
    __tablename__ = 'debt'

    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    transactionid = Column(Integer, ForeignKey('issuedbooks.transactionid'))
    amountdue = Column(Integer, default=0)
    paid = Column(Boolean, default=False)

    def __repr__(self):
        return "<Debt(EntryID='%d', TransactionId='%d', AmountDue='%d', Paid='%s')>" % (self.entry_id, self.transactionid, self.amountdue, self.paid)
    
class BookIssue(Base):
    __tablename__ = 'issuedbooks'
    
    transactionid = Column(Integer, primary_key=True, autoincrement=True)
    bookid = Column(Integer, ForeignKey('books.bookid'))
    memberid = Column(Integer, ForeignKey('members.memberid'))
    created_on = Column(Date, default=datetime.date.today())
    issued_date = Column(Date, default=datetime.date.today())
    returned_date = Column(Date)
    active = Column(Boolean, default=True)
    
    # Charging rent
    charge = relationship("Debt", backref="transaction", uselist=False)

    def __repr__(self):
        return "<BookIssue(transactionid={}', bookid={}, memberid={}, created_on={}, issued_date={}, returned_date={}, active={})>".format(self.transactionid, self.bookid, self.memberid, None if self.created_on == None else self.created_on.strftime("%Y-%m-%d"), None if self.issued_date == None else self.issued_date.strftime("%Y-%m-%d"), None if self.returned_date == None else self.returned_date.strftime("%Y-%m-%d"), self.active)

def init_book_stock(app):
    # initialize book stock
    session = app.config['DB_SESSIONMAKER']()
    books = flask.json.loads(app.open_resource("db_init_stock.json").read())
    for x in books:
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
        click.echo('Book stock has been initialized')
    except Exception as unknown:
        click.echo('Unable to initialize book stock')

    session.close()
    
def init_db(app):
    Base.metadata.drop_all(app.config['DB_ENGINE'])
    Base.metadata.create_all(app.config['DB_ENGINE'])
    app.config.from_mapping(
        DB_SESSION = app.config['DB_SESSIONMAKER']()
    )
    

def init_cli_command(app):
    @app.cli.command('init-db')
    def init_db_command():
        init_db(app)
        click.echo('Database initialized')
        init_book_stock(app)

    app.cli.add_command(init_db_command)

def init_db_command(app):
    init_db(app)
    click.echo('Database initialized.')
    init_book_stock(app);
    
def configure_session(app):
    # add cli command for database initialization
    init_cli_command(app)
    
    if app.config['TESTING'] == True:
        # engine = create_engine("sqlite:///"+app.config['DATABASE'])
        engine = create_engine('sqlite:///:memory:',
                               connect_args={"check_same_thread": False},
                               poolclass=StaticPool)
    else:
        engine = create_engine("sqlite:///" + app.config['DATABASE'],
                               connect_args={"check_same_thread": False})

    Session = sessionmaker(bind=engine)
    app.config.from_mapping(
        DB_ENGINE = engine,
        DB_SESSIONMAKER = Session
    )

    # If in testing mode, create a temporary database
    if app.config['TESTING'] == True:
        init_db(app)

