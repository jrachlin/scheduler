import os
import logging
from datetime import datetime
from multiprocessing import Process

import config
from core.message import Message


logger = logging.getLogger(__name__)


class Task(Process):
    def __init__(self, name, script, time, dependencies={}, queue=None):
        """
        Initialize object.
        :param str name: Routine name
        :param str script: Full path to python script to run
        :param datetime time: The time that the task is supposed to run at
        :param dict dependencies: A dictionary of dependencies keys are qualified names, values are state information
        :param queue queue: A queue object
        """
        super().__init__(name=name)
        self.script = script
        self.time = time
        self.qualified_name = '.'.join([self.name, self.get_time_str()])
        self.dependencies = dependencies
        self.result_queue = queue
        self.state = 'Waiting' if self.dependencies else 'Ready'

        # Identify routine log directory and set log file path
        log_directory = config.get_config_file().get('DEFAULT', 'log_directory')
        routine_directory = os.path.join(log_directory, self.name)
        if not os.path.exists(routine_directory):
            os.makedirs(routine_directory)
        # Standard time format uses :, but that cannot be used in a file name so replace.
        log_file_name = '.'.join([self.name, self.get_time_str().replace(':','-'), 'log'])
        self.log = os.path.join(routine_directory, log_file_name)

    def __lt__(self, other):
        """Order tasks based on time parameter"""
        return self.time < other.time

    def __gt__(self, other):
        """Order tasks based on time parameter"""
        return self.time > other.time

    def get_time_str(self):
        """Returns task time in standard string format"""
        return self.time.strftime(config.dt_format_str)

    def update_state(self, new_state):
        """
        Update internal task state and send a message to the queue with this update
        :param str new_state: The new state
        """
        self.state = new_state
        if self.result_queue:
            self.send_message(new_state)

    def send_message(self, state):
        """
        Create new state message and put into queue
        :param str state: the new state
        """
        if self.result_queue:
            m = Message(name=self.name, time=self.time, qualified_name=self.qualified_name,
                        state=state, time_stamp=datetime.today())
            self.result_queue.put(m)

    def update_dependency_state(self, qualified_name, new_state):
        """
        Update the state of one of the tasks this task waits on.  Then check whether that update implies any action
        for this task.
        :param str qualified_name: The dependency qualified name
        :param str new_state: The new state of the dependency
        """
        self.dependencies[qualified_name] = new_state  # Update the state information
        # If all dependencies are now successful, this task is ready to be executed.
        if all([dep_state == 'Success' for dep_state in self.dependencies.values()]):
            self.update_state('Ready')
        # If the new state is cancelled, cancel this task
        elif new_state == 'Cancelled':
            self.update_state('Cancelled')

    def run(self):
        """
        Execute the script in a separate process
        """
        # We want the logging of the individual tasks to be separate from the main program.  So that logging
        # configuration is handled here.
        logging.basicConfig(filename=self.log, level=logging.DEBUG,
                            format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                            datefmt=config.dt_format_str)
        logger = logging.getLogger(__name__)

        logger.info('Running %s', self.qualified_name)
        try:
            exec(open(self.script).read())
            result = 'Success'
            logger.info('Success')
        except Exception as e:
            result = 'Failure'
            logger.exception('Encountered an error running: ' + self.script)
        # Send the result to the queue for processing by the main program
        self.update_state(result)