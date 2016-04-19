from .common import *


class GetHistoricalMeetsByDateTest(EntityTest):

	@classmethod
	def setUpClass(cls):

		cls.meets = pyracing.Meet.get_meets_by_date(historical_date)

	def test_types(self):
		"""The get_meets_by_date method should return a list of Meet objects"""

		self.check_types(self.meets, list, pyracing.Meet)

	def test_ids(self):
		"""All Meet objects returned by get_meets_by_date should have a database ID"""
		
		self.check_ids(self.meets)

	def test_scraped_at_dates(self):
		"""All Meet objects returned by get_meets_by_date should have a scraped_at date"""
		
		self.check_scraped_at_dates(self.meets)

	def test_no_rescrape(self):
		"""Subsequent calls to get_meets_by_date for the same historical date should retrieve data from the database"""

		self.check_no_rescrape(pyracing.Meet.get_meets_by_date, historical_date)


class GetFutureMeetsByDateTest(EntityTest):

	def test_rescrape(self):
		"""Subsequent calls to get_meets_by_date for the same future date should replace data in the database"""

		self.check_rescrape(pyracing.Meet.get_meet_by_id, pyracing.Meet.get_meets_by_date, future_date)