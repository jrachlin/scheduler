import os
import logging
from datetime import datetime
from multiprocessing import Process

import config
from core.message import Message


logger = logging.getLogger(__name__)


def qualified_task_name(task_name, time):
    time_str = time.strftime(config.dt_format_str)
    return '.'.join([task_name, time_str])


class Task(Process):
    def __init__(self, name, script, time, dependencies={}, queue=None):
        """
        Args:
            name (str): Routine name
            script (str): Full path to python executable
            time (datetime): The time at which the task is supposed to run
            dependencies (dict): A dictionary of dependencies. Keys are qualified names, values are state information
            queue (Queue): A queue object. Used to communicate results.
        """
        super().__init__(name=name)
        self.script = script
        self.time = time
        self.qualified_name = qualified_task_name(self.name, self.time)
        self.dependencies = dependencies
        self.result_queue = queue
        self.state = 'Waiting' if self.dependencies else 'Ready'

        # Identify routine log directory and set log file path
        log_directory = config.get_config_file().get('DEFAULT', 'log_directory')
        routine_directory = os.path.join(log_directory, self.name)
        if not os.path.exists(routine_directory):
            os.makedirs(routine_directory)
        # Standard time format uses :, but that cannot be used in a file name so replace.
        log_file_name = '.'.join([self.qualified_name.replace(':', '-'), 'log'])
        self.log = os.path.join(routine_directory, log_file_name)

    def __lt__(self, other):
        """Order tasks based on time parameter"""
        return self.time < other.time

    def __gt__(self, other):
        """Order tasks based on time parameter"""
        return self.time > other.time

    def update_state(self, new_state):
        """
        Update internal task state and send a message to the queue with this update

        Args:
            new_state (str): The new state
        """
        self.state = new_state
        if self.result_queue:
            self.send_message(new_state)

    def send_message(self, state):
        """
        Create new state message and put into queue

        Args:
            state (str): the new state
        """
        m = Message(name=self.name, time=self.time, qualified_name=self.qualified_name,
                    state=state, time_stamp=datetime.today())
        self.result_queue.put(m)

    def update_dependency_state(self, qualified_name, new_state):
        """
        Update the state of one of the tasks this task waits on.  Then check whether that update implies any action
        for this task.

        Args:
            qualified_name (str): The dependency qualified name
            new_state (str): The new state of the dependency
        """
        # Update dependency state information
        self.dependencies[qualified_name] = new_state
        # If all dependencies are now successful, this task is ready to be executed.
        if all([dep_state == 'Success' for dep_state in self.dependencies.values()]):
            self.update_state('Ready')

    def run(self):
        """
        Execute the script in a separate process
        """
        # We want the logging of the individual tasks to be separate from the main program.  So that logging
        # configuration is handled here.
        logging.basicConfig(filename=self.log, level=logging.DEBUG,
                            format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                            datefmt=config.dt_format_str)
        task_logger = logging.getLogger(__name__)

        task_logger.info('Running %s', self.qualified_name)
        try:
            exec(open(self.script).read())
            result = 'Success'
            task_logger.info('Success')
        except Exception as e:
            result = 'Failure'
            task_logger.exception('Encountered an error running: ' + self.script)
            task_logger.exception(e)
        # Send the result to the queue for processing by the main program
        self.update_state(result)
