from datetime import datetime

import config
from core.schedule import Schedule
from core.task import Task


class Routine:
    def __init__(self, name, script=None, schedule=None):
        """
        Initialize object.
        :param str name: Name of the routine
        :param str script: Path of script to be run by the routine
        :param str schedule: a cron-like string
        """
        self.dependants = set()  # routines that depend on this routine
        self.dependencies = set()  # routines that this routine depends on
        self.name = name
        self.script = script
        self.schedule = Schedule(schedule) if schedule else schedule

    def next_trigger(self, reference_point, inclusive=False):
        """
        Return the next runtime
        :param datetime reference_point: Next means relative to this datetime
        :param bool inclusive: if True, include the reference_point as a valid next datetime
        :return: datetime
        """
        # If the task has a schedule, then find the next scheduled runtime
        if self.schedule:
            return self.schedule.next(reference_point, inclusive)
        # If the task has no schedule, but simply runs after its dependencies, then use their last next runtime
        elif self.dependencies:
            return max([k.next_trigger(reference_point, inclusive) for k in self.dependencies])
        # Otherwise, this is really only manually triggered
        else:
            return datetime(9999,12,31)

    def previous_trigger(self, reference_point, inclusive=False):
        """
        Return the previous runtime
        :param datetime reference_point: Next means relative to this datetime
        :param bool inclusive: if True, include the reference_point as a valid next datetime
        :return: datetime
        """
        # If the task has a schedule, then find the previous scheduled runtime
        if self.schedule:
            return self.schedule.previous(reference_point, inclusive)
        # If the task has no schedule, but simply runs after its dependencies, then use their last previous runtime
        elif self.dependencies:
            return max([k.previous_trigger(reference_point, inclusive) for k in self.dependencies])
        # Otherwise, this is really only manually triggered
        else:
            return datetime(9999, 12, 31)

    def depends_on(self, other):
        """
        Register a dependency between routines
        :param other: the routine this routine depends on (waits for)
        """
        self.dependencies.add(other)
        other.dependants.add(self)

    def next_task(self, reference_point, queue=None):
        """
        Returns a task object representing the next task instance
        :param datetime reference_point: Next task time will be judged relative to this reference point
        :param Queue queue: The queue the task should provide updates through
        :return: Task
        """
        time = self.next_trigger(reference_point)
        dependencies = {}
        for dep in self.dependencies:
            dep_time = dep.previous_trigger(time, inclusive=True)
            dep_time = dep_time.strftime(config.dt_format_str)
            dependencies['.'.join([dep.name, dep_time])] = None
        return Task(self.name, self.script, time, dependencies, queue=queue)

