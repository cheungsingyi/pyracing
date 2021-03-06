from .common import *


class GetHistoricalHorseByRunnerTest(EntityTest):

	@classmethod
	def setUpClass(cls):

		cls.meet = pyracing.Meet.get_meets_by_date(historical_date)[0]
		cls.race = cls.meet.races[0]
		cls.runner = cls.race.runners[0]
		cls.horse = pyracing.Horse.get_horse_by_runner(cls.runner)

	def test_type(self):
		"""The get_horse_by_runner method should return a single Horse object"""

		self.assertIsInstance(self.horse, pyracing.Horse)

	def test_id(self):
		"""The Horse object returned by get_horse_by_runner should have a database ID"""
		
		self.check_ids([self.horse])

	def test_scraped_at_date(self):
		"""The Horse object returned by get_horse_by_runner should have a scraped_at date"""
		
		self.check_scraped_at_dates([self.horse])

	def test_no_rescrape(self):
		"""Subsequent calls to get_horse_by_runner for the same historical runner should retrieve data from the database"""

		new_horse = pyracing.Horse.get_horse_by_runner(self.runner)

		self.assertEqual(self.horse['_id'], new_horse['_id'])


class GetFutureHorseByRunnerTest(EntityTest):

	def test_rescrape(self):
		"""Subsequent calls to get_horse_by_runner for the same future runner should replace data in the database"""

		meet = pyracing.Meet.get_meets_by_date(future_date)[0]
		race = meet.races[0]
		runner = race.runners[0]
		old_horse = pyracing.Horse.get_horse_by_runner(runner)

		pyracing.Entity.SESSION_ID = datetime.now()

		new_horse = pyracing.Horse.get_horse_by_runner(runner)

		self.assertNotEqual(old_horse['_id'], new_horse['_id'])


class HorsePropertiesTest(EntityTest):

	def test_performances(self):
		"""The performances property should return a list of performances involving the horse"""

		meet = pyracing.Meet.get_meets_by_date(historical_date)[0]
		race = meet.races[0]
		runner = race.runners[0]

		self.assertEqual(pyracing.Performance.get_performances_by_horse(runner.horse), runner.horse.performances)


class DeleteHorseTest(EntityTest):

	def test_deletes_performances(self):
		"""Deleting a horse should also delete any performances involving that horse"""

		meet = pyracing.Meet.get_meets_by_date(historical_date)[0]
		race = meet.races[0]
		runner = race.runners[0]
		old_ids = [performance['_id'] for performance in runner.horse.performances]

		runner.horse.delete()

		for old_id in old_ids:
			self.assertIsNone(pyracing.Performance.get_performance_by_id(old_id))