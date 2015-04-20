# Imports
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

# Metadata
Base = declarative_base()
Engine = create_engine('sqlite:///data.db')

# Tables
class Ticker(Base):
	"""The parent "table declarative" class"""
	__tablename__ = 'tickers'
	id = Column(Integer, primary_key = True)
	name = Column(String(20), nullable = False)
	earnings_dates = relationship("EarningsDay", backref = "tickers")

class EarningsDay(Base):
	"""The table which containts earnings dates data"""
	__tablename__ = 'earnings_dates'
	id = Column(Integer, primary_key = True)
	date = Column(String(20), nullable = False)
	ticker_id = Column(Integer, ForeignKey('tickers.id'))
	ticker = relationship(Ticker, backref = backref('tickers', uselist=True))

# Creation
Base.metadata.create_all(Engine)

