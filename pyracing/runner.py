from datetime import timedelta

from .common import Entity
from .performance_list import PerformanceList


class Runner(Entity):
	"""A runner represents a combination of horse, jockey and trainer competing in a given race"""

	REST_PERIOD = timedelta(days=90)

	@classmethod
	def get_runner_by_id(cls, id):
		"""Get the single runner with the specified database ID"""

		return cls.find_one({'_id': id})

	@classmethod
	def get_runners_by_race(cls, race):
		"""Get a list of runners competing in the specified race"""

		runners = sorted(cls.find_or_scrape(
			filter={'race_id': race['_id']},
			scrape=cls.scraper.scrape_runners,
			scrape_args=[race],
			expiry_date=race['start_time']
			), key=lambda runner: runner['number'])

		for runner in runners:
			if not 'race_id' in runner:
				runner['race_id'] = race['_id']
				runner.save()

		return runners

	@classmethod
	def initialize(cls):
		"""Initialize class dependencies"""

		def handle_deleting_race(race):
			for runner in race.runners:
				runner.delete()

		cls.event_manager.add_subscriber('deleting_race', handle_deleting_race)

		cls.create_index([('race_id', 1)])
		cls.create_index([('race_id', 1), ('scraped_at', 1)])

	def __str__(self):

		return 'runner {number} in {race}'.format(number=self['number'], race=self.race)

	@property
	def actual_weight(self):
		"""Return the weight carried by the runner plus the average weight of a racehorse"""

		if self.carrying is not None:
			return self.carrying + Horse.AVERAGE_WEIGHT

	@property
	def age(self):
		"""Return the horse's official age as at the time of the race"""

		if 'foaled' in self.horse and self.horse['foaled'] is not None:
			birthday = self.horse['foaled'].replace(month=8, day=1)
			return (self.race.meet['date'] - birthday).days // 365

	@property
	def at_distance(self):
		"""Return a PerformanceList containing all of the horse's prior performances within 100m of the current race's distance"""

		if not 'at_distance' in self.cache:
			self.cache['at_distance'] = PerformanceList([performance for performance in self.career if self.race['distance'] - 100 <= performance['distance'] <= self.race['distance'] + 100])
		return self.cache['at_distance']

	@property
	def at_distance_on_track(self):
		"""Return a PerformanceList containing all of the horse's prior performances within 100m of the current race's distance on the current track"""

		if not 'at_distance_on_track' in self.cache:
			self.cache['at_distance_on_track'] = PerformanceList([performance for performance in self.at_distance if performance in self.on_track])
		return self.cache['at_distance_on_track']

	@property
	def career(self):
		"""Return a PerformanceList containing all of the horse's performances prior to the current race"""

		if not 'career' in self.cache:
			self.cache['career'] = PerformanceList([performance for performance in self.horse.performances if performance['date'] < self.race.meet['date']])
		return self.cache['career']

	@property
	def carrying(self):
		"""Return the official listed weight less allowances for the runner"""

		if 'weight' in self and self['weight'] is not None and 'jockey_claiming' in self and self['jockey_claiming'] is not None:
			return self['weight'] - self['jockey_claiming']

	@property
	def current_performance(self):
		"""Return the horse's performance for the current race if available"""

		for performance in self.horse.performances:
			if performance['track'] == self.race.meet['track'] and performance['date'] == self.race.meet['date']:
				return performance

	@property
	def firm(self):
		"""Return a PerformanceList containing all of the horse's prior performances on firm tracks"""

		if not 'firm' in self.cache:
			self.cache['firm'] = self.get_performances_by_track_condition('firm')
		return self.cache['firm']

	@property
	def good(self):
		"""Return a PerformanceList containing all of the horse's prior performances on good tracks"""

		if not 'good' in self.cache:
			self.cache['good'] = self.get_performances_by_track_condition('good')
		return self.cache['good']

	@property
	def heavy(self):
		"""Return a PerformanceList containing all of the horse's prior performances on heavy tracks"""

		if not 'heavy' in self.cache:
			self.cache['heavy'] = self.get_performances_by_track_condition('heavy')
		return self.cache['heavy']

	@property
	def horse(self):
		"""Return the actual horse running in the race"""

		if not 'horse' in self.cache:
			self.cache['horse'] = Horse.get_horse_by_runner(self)
		return self.cache['horse']

	@property
	def jockey(self):
		"""Return the actual jockey riding in the race"""

		if not 'jockey' in self.cache:
			self.cache['jockey'] = Jockey.get_jockey_by_runner(self)
		return self.cache['jockey']

	@property
	def jockey_at_distance(self):
		"""Return a PerformanceList containing all of the jockey's prior performances within 100m of the current race's distance"""

		if not 'jockey_at_distance' in self.cache:
			self.cache['jockey_at_distance'] = PerformanceList([performance for performance in self.jockey_career if self.race['distance'] - 100 <= performance['distance'] <= self.race['distance'] + 100])
		return self.cache['jockey_at_distance']

	@property
	def jockey_at_distance_on_track(self):
		"""Return a PerformanceList containing all of the jockey's prior performances within 100m of the current race's distance on the current track"""

		if not 'jockey_at_distance_on_track' in self.cache:
			self.cache['jockey_at_distance_on_track'] = PerformanceList([performance for performance in self.jockey_at_distance if performance in self.jockey_on_track])
		return self.cache['jockey_at_distance_on_track']

	@property
	def jockey_career(self):
		"""Return a PerformanceList containing all of the jockey's performances prior to the current race"""

		if not 'jockey_career' in self.cache:
			if self.jockey is not None:
				self.cache['jockey_career'] = PerformanceList([performance for performance in self.jockey.performances if performance['date'] < self.race.meet['date']])
			else:
				self.cache['jockey_career'] = PerformanceList()
		return self.cache['jockey_career']

	@property
	def jockey_firm(self):
		"""Return a PerformanceList containing all of the jockey's prior performances on firm tracks"""

		if not 'jockey_firm' in self.cache:
			self.cache['jockey_firm'] = self.get_jockey_performances_by_track_condition('firm')
		return self.cache['jockey_firm']

	@property
	def jockey_good(self):
		"""Return a PerformanceList containing all of the jockey's prior performances on good tracks"""

		if not 'jockey_good' in self.cache:
			self.cache['jockey_good'] = self.get_jockey_performances_by_track_condition('good')
		return self.cache['jockey_good']

	@property
	def jockey_heavy(self):
		"""Return a PerformanceList containing all of the jockey's prior performances on heavy tracks"""

		if not 'jockey_heavy' in self.cache:
			self.cache['jockey_heavy'] = self.get_jockey_performances_by_track_condition('heavy')
		return self.cache['jockey_heavy']

	@property
	def jockey_on_track(self):
		"""Return a PerformanceList containing all of the jockey's prior performances on the current track"""

		if not 'jockey_on_track' in self.cache:
			self.cache['jockey_on_track'] = PerformanceList([performance for performance in self.jockey_career if performance['track'] == self.race.meet['track']])
		return self.cache['jockey_on_track']

	@property
	def jockey_soft(self):
		"""Return a PerformanceList containing all of the jockey's prior performances on soft tracks"""

		if not 'jockey_soft' in self.cache:
			self.cache['jockey_soft'] = self.get_jockey_performances_by_track_condition('soft')
		return self.cache['jockey_soft']

	@property
	def jockey_synthetic(self):
		"""Return a PerformanceList containing all of the jockey's prior performances on synthetic tracks"""

		if not 'jockey_synthetic' in self.cache:
			self.cache['jockey_synthetic'] = self.get_jockey_performances_by_track_condition('synthetic')
		return self.cache['jockey_synthetic']

	@property
	def on_track(self):
		"""Return a PerformanceList containing all of the horse's prior performances on the current track"""

		if not 'on_track' in self.cache:
			self.cache['on_track'] = PerformanceList([performance for performance in self.career if performance['track'] == self.race.meet['track']])
		return self.cache['on_track']

	@property
	def on_up(self):
		"""Return a PerformanceList containing all of the horse's prior performances with the same UP number"""

		if not 'on_up' in self.cache:

			performances = []
			previous_date = None
			up = 0
			for index in range(len(self.career) - 1, 0, -1):
				if previous_date is None or ((self.career[index]['date'] - previous_date) < self.REST_PERIOD):
					up += 1
				else:
					up = 1
				if up == self.up:
					performances.append(self.career[index])
				previous_date = self.career[index]['date']

			self.cache['on_up'] = PerformanceList(performances)

		return self.cache['on_up']

	@property
	def race(self):
		"""Return the race in which this runner competes"""

		if not 'race' in self.cache:
			self.cache['race'] = Race.get_race_by_id(self['race_id'])
		return self.cache['race']

	@property
	def result(self):
		"""Return the final result for this runner if available"""

		if self.current_performance is not None:
			if self.current_performance['result'] is not None:
				return self.current_performance['result']
			else:
				return self.current_performance['starters']

	@property
	def since_rest(self):
		"""Return a PerformanceList containing the horse's prior performances since the last spell of 90 days or more"""

		if not 'since_rest' in self.cache:

			performances = []
			next_date = self.race.meet['date']
			for index in range(len(self.career)):
				if (next_date - self.career[index]['date']) < self.REST_PERIOD:
					performances.append(self.career[index])
					next_date = self.career[index]['date']
				else:
					break

			self.cache['since_rest'] = PerformanceList(performances)

		return self.cache['since_rest']

	@property
	def soft(self):
		"""Return a PerformanceList containing all of the horse's prior performances on soft tracks"""

		if not 'soft' in self.cache:
			self.cache['soft'] = self.get_performances_by_track_condition('soft')
		return self.cache['soft']

	@property
	def spell(self):
		"""Return the number of days since the horse's previous run"""

		if len(self.career) > 0:
			return (self.race.meet['date'] - self.career[0]['date']).days

	@property
	def starting_price(self):
		"""Return the starting price for this runner if available"""

		if self.current_performance is not None:
			if 'starting_price' in self.current_performance:
				return self.current_performance['starting_price']

	@property
	def synthetic(self):
		"""Return a PerformanceList containing all of the horse's prior performances on synthetic tracks"""

		if not 'synthetic' in self.cache:
			self.cache['synthetic'] = self.get_performances_by_track_condition('synthetic')
		return self.cache['synthetic']

	@property
	def trainer(self):
		"""Return the trainer responsible for the runner"""

		if not 'trainer' in self.cache:
			self.cache['trainer'] = Trainer.get_trainer_by_runner(self)
		return self.cache['trainer']

	@property
	def up(self):
		"""Return the number of races run by the horse (including this one) since the last rest period of 90 days or more"""

		up = 1

		next_date = self.race.meet['date']
		for index in range(len(self.career)):
			if (next_date - self.career[index]['date']) < self.REST_PERIOD:
				up += 1
				next_date = self.career[index]['date']
			else:
				break

		return up

	@property
	def with_jockey(self):
		"""Return a PerformanceList containing all of the horse's prior performances with the same jockey"""

		if not 'with_jockey' in self.cache:
			self.cache['with_jockey'] = PerformanceList([performance for performance in self.career if performance['jockey_url'] == self['jockey_url']])
		return self.cache['with_jockey']

	def calculate_expected_speed(self, performance_list):
		"""Return a tuple containing expected speeds based on the minimum, maximum and average momentums for the specified performance list"""

		performance_list = getattr(self, performance_list)
		if performance_list is not None:

			expected_speeds = [None, None, None]

			if self.actual_weight is not None and self.actual_weight > 0:
				if performance_list.minimum_momentum is not None:
					expected_speeds[0] = performance_list.minimum_momentum / self.actual_weight
				if performance_list.maximum_momentum is not None:
					expected_speeds[1] = performance_list.maximum_momentum / self.actual_weight
				if performance_list.average_momentum is not None:
					expected_speeds[2] = performance_list.average_momentum / self.actual_weight

			return tuple(expected_speeds)

	def get_performances_by_track_condition(self, track_condition):
		"""Return a PerformanceList containing all prior performances for the horse on the specified track condition"""

		return PerformanceList([performance for performance in self.career if performance['track_condition'].upper().startswith(track_condition.upper())])

	def get_jockey_performances_by_track_condition(self, track_condition):
		"""Return a PerformanceList containing all prior performances for the jockey on the specified track condition"""

		return PerformanceList([performance for performance in self.jockey_career if performance['track_condition'].upper().startswith(track_condition.upper())])


from .race import Race
from .horse import Horse
from .jockey import Jockey
from .trainer import Trainer
