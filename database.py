import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime

from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declarative_base()
# create State table
class Accounts(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    password = Column(String(250))
    


# create TouristPlace Table
class Books(Base):
    __tablename__ = 'books'

   
    id = Column(Integer, primary_key=True)
    isbn = Column(String(30),nullable=False)
    title = Column(String(50),nullable=False)
    author = Column(String(30),nullable=False)
    year = Column(Integer,nullable=False)
    
    
class Reviews(Base):
    __tablename__ = 'reviews'

   
    id = Column(Integer, primary_key=True)
    acc_id = Column(String(30),nullable=False)
    book_id = Column(String(50),nullable=False)
    comment = Column(String(30),nullable=False)
    rating = Column(Integer,nullable=False)
    date= Column(DateTime)
    reviews_acc_id_fkey = Column(Integer, ForeignKey('accounts.id'))
    accounts = relationship(Accounts)
    reviews_book_id_fkey = Column(Integer, ForeignKey('books.id'))
    books = relationship(Books)
    
engine = create_engine('sqlite:///books.db')
Base.metadata.create_all(engine)