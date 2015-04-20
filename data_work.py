from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_declaration import Base, Ticker, EarningsDay

class DataManager(object):
	"""Manages the database work for the script"""
	def __init__(self,):
		self.db_location = 'sqlite:///data.db'
		self.engine = create_engine(self.db_location)
		Base.metadata.bind = self.engine
		self.DBsession = sessionmaker(bind=self.engine)
		self.session = self.DBsession()

data_manager = DataManager()

