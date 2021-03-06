class PerformanceList(list):
	"""A PerformanceList represents a filtered list of performances decorated with statistical calculations"""

	def __init__(self, *args, **kwargs):
		"""Create PerformanceList and ensure it is sorted by date in descending order"""
		super().__init__(*args, **kwargs)

		self.sort(key=lambda performance: performance['date'], reverse=True)

		self.calculate_average = self.calculate_percentage

	@property
	def average_momentum(self):
		"""Return the average momentum per start in this performance list"""

		momentums = self.get_momentums()
		if len(momentums) > 0:
			return self.calculate_average(sum(momentums))

	@property
	def average_prize_money(self):
		"""Return the average prize money per start in this performance list"""

		return self.calculate_average(self.total_prize_money)

	@property
	def average_starting_price(self):
		"""Return the average starting price per start in this performance list"""

		starting_prices = [performance['starting_price'] for performance in self if performance['starting_price'] is not None]
		if len(starting_prices) > 0:
			return self.calculate_average(sum(starting_prices))

	@property
	def fourths(self):
		"""Return the number of fourth placing performances included in this performance list"""

		return self.count_results(4)

	@property
	def fourth_pct(self):
		"""Return the number of fourths as a percentage of the number of starts"""

		return self.calculate_percentage(self.fourths)

	@property
	def maximum_momentum(self):
		"""Return the maximum momentum achieved for any performance in this list"""

		momentums = self.get_momentums()
		if len(momentums) > 0:
			return max(momentums)

	@property
	def minimum_momentum(self):
		"""Return the minimum momentum achieved for any performance in this list"""

		momentums = self.get_momentums()
		if len(momentums) > 0:
			return min(momentums)

	@property
	def places(self):
		"""Return the number of placing (1st, 2nd and 3rd) performances included in this performance list"""

		if self.wins is not None and self.seconds is not None and self.thirds is not None:
			return self.wins + self.seconds + self.thirds

	@property
	def place_pct(self):
		"""Return the number of places as a percentage of the number of starts"""

		return self.calculate_percentage(self.places)

	@property
	def roi(self):
		"""Return the total starting price for winning performances less the total number of performances in the list, expressed as a percentage of the number of starts"""

		winning_starting_prices = [performance['starting_price'] for performance in self if performance['result'] == 1 and performance['starting_price'] is not None]
		if len(winning_starting_prices) > 0:
			return self.calculate_percentage(sum(winning_starting_prices) - self.starts)

	@property
	def seconds(self):
		"""Return the number of second placing performances included in this performance list"""

		return self.count_results(2)

	@property
	def second_pct(self):
		"""Return the number of seconds as a percentage of the number of starts"""

		return self.calculate_percentage(self.seconds)

	@property
	def starts(self):
		"""Return the number of starts included in this performance list"""

		return len(self)

	@property
	def thirds(self):
		"""Return the number of third placing performances included in this performance list"""

		return self.count_results(3)

	@property
	def third_pct(self):
		"""Return the number of thirds as a percentage of the number of starts"""

		return self.calculate_percentage(self.thirds)

	@property
	def total_prize_money(self):
		"""Return the total prize money earned in this performance list"""

		runner_prize_monies = [performance['runner_prize_money'] for performance in self if performance['runner_prize_money'] is not None]
		if len(runner_prize_monies) > 0:
			return sum(runner_prize_monies)

	@property
	def wins(self):
		"""Return the number of winning performances included in this performance list"""

		return self.count_results(1)

	@property
	def win_pct(self):
		"""Return the number of wins as a percentage of the number of starts"""

		return self.calculate_percentage(self.wins)

	def calculate_percentage(self, value, divide_by_zero=None):
		"""Return the specified value expressed as a percentage of the number of starts

		If the number of starts is 0, return divide_by_zero instead.
		"""

		if value is not None:
			if self.starts > 0:
				return value / self.starts
			else:
				return divide_by_zero

	def count_results(self, result):
		"""Return the number of performances in this list with the specified result"""

		return len([performance for performance in self if performance['result'] == result])

	def get_momentums(self):
		"""Return an array containing the momentums for all performances in this list"""

		return [performance.momentum for performance in self if performance.momentum is not None]