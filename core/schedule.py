import datetime

class Schedule:
    """
    Object representing a series of moments as defined by standard cron text
    * * * * * = > [minute] [hour] [day of month] [month] [day of week]
    """
    def __init__(self, cron_string):
        """
        Initialize object.
        :param str cron_string: a cron like string
        """
        input_list = [int(k) if k != '*' else k for k in cron_string.split(' ')]
        label_list = ['minute', 'hour', 'day', 'month', 'weekday']

        self.specs = dict(zip(label_list, input_list))
        assert(self.specs['minute'] == '*' or 0 <= self.specs['minute'] <= 59)
        assert(self.specs['hour'] == '*' or 0 <= self.specs['hour'] <= 23)
        assert(self.specs['day'] == '*' or 1 <= self.specs['day'] <= 31)
        assert(self.specs['month'] == '*' or 1 <= self.specs['month'] <= 12)
        assert(self.specs['weekday'] == '*' or 0 <= self.specs['weekday'] <= 6)

    def next(self, reference=None, inclusive=False):
        """
        Returns the next valid datetime according to schedule.
        :param reference: Next implies next valid datetime from this reference datetime
        :param inclusive: Whether to consider the reference datetime a valid return value
        :return: datetime
        """
        if reference is None:
            reference = datetime.datetime.today()

        next = reference.replace(second=0, microsecond=0)
        if not inclusive:
            next = next + datetime.timedelta(minutes=1)
        while True:
            if (self.specs['month'] != '*' and next.month != self.specs['month']):
                next_year = next.year if next.month != 12 else next.year + 1
                next_month = next.month + 1 if next.month != 12 else 1
                next = next.replace(year=next_year, month=next_month, day=1, hour=0, minute=0)
            elif (self.specs['day'] != '*' and next.day != self.specs['day']):
                next = next.replace(hour=0, minute=0) + datetime.timedelta(days=1)
            elif (self.specs['weekday'] != '*' and next.weekday() != self.specs['weekday']):
                next = next.replace(hour=0, minute=0) + datetime.timedelta(days=1)
            elif (self.specs['hour'] != '*' and next.hour != self.specs['hour']):
                next = next.replace(minute=0) + datetime.timedelta(hours=1)
            elif (self.specs['minute'] != '*' and next.minute != self.specs['minute']):
                next = next + datetime.timedelta(minutes=1)
            else:
                return next

    def previous(self, reference=None, inclusive=False):
        """
        Returns the previous valid datetime according to schedule.
        :param reference: Previous implies previous valid datetime from this reference datetime
        :param inclusive: Whether to consider the reference datetime a valid return value
        :return: datetime
        """
        if reference is None:
            reference = datetime.datetime.today()

        previous = reference.replace(second=0, microsecond=0)
        if not inclusive:
            previous = previous - datetime.timedelta(minutes=1)
        while True:
            if (self.specs['month'] != '*' and previous.month != self.specs['month']):
                previous = previous.replace(day=1, hour=23, minute=59) - datetime.timedelta(days=1)
            elif (self.specs['day'] != '*' and previous.day != self.specs['day']):
                previous = previous.replace(hour=23, minute=59) - datetime.timedelta(days=1)
            elif (self.specs['weekday'] != '*' and previous.weekday() != self.specs['weekday']):
                previous = previous.replace(hour=23, minute=59) - datetime.timedelta(days=1)
            elif (self.specs['hour'] != '*' and previous.hour != self.specs['hour']):
                previous = previous.replace(minute=59) - datetime.timedelta(hours=1)
            elif (self.specs['minute'] != '*' and previous.minute != self.specs['minute']):
                previous = previous - datetime.timedelta(minutes=1)
            else:
                return previous
