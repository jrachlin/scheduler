# Standard library imports
import time
import bisect
import logging
from datetime import datetime

# Internal imports
import config
from core.task import Task
from core.message import Message


logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self, event_queue, state_manager, registry, config):
        self.registry = registry
        self.event_queue = event_queue
        self.state_manager = state_manager
        self.config = config
        self.running_tasks = []
        self.scheduled_tasks_dict = {}
        self.scheduled_tasks_list = []
        self.task_dependencies = {}
        self.keep_running = True

    def launch(self, resume):
        if resume:
            last_shutdown = self.config.get('DEFAULT', 'last_shutdown')
            reference_time = datetime.strptime(last_shutdown, config.dt_format_str)
            logger.info('Resuming as of last shutdown: %s', last_shutdown)
        else:
            self.config['DEFAULT']['last_shutdown'] = ''
            reference_time = datetime.today()
        logger.info('Scheduling All Jobs')
        if resume:
            # Retrieve previously scheduled tasks
            last_instance = {}
            for row in self.state_manager.get_current_status():
                routine, instance, state, state_time_stamp = row
                if state in ['READY', 'WAITING']:
                    last_instance[routine] = instance
        for name, routine in self.registry:
            if resume:
                resume_instance = last_instance.get(name)
                if resume_instance:
                    self.schedule_next_task(routine, resume_instance)
                    continue
            self.schedule_next_task(routine, reference_time)
        self.main_loop()

    def schedule_next_task(self, routine, reference_time):
        task = routine.next_task(reference_time, self.event_queue)
        logger.info('Scheduling Next: %s', task.qualified_name)
        if task.qualified_name in self.scheduled_tasks_dict.keys():
            logger.info('Already scheduled, skipping: %s', task.qualified_name)
            return
        self.scheduled_tasks_dict[task.qualified_name] = task
        bisect.insort(self.scheduled_tasks_list, task)
        self.state_manager.update(task.name, task.time, task.state)
        self.register_dependencies(task, reference_time)

    def register_dependencies(self, task, reference_time):
        cancel = False
        for dependency in task.dependencies:
            if dependency in self.task_dependencies:
                self.task_dependencies[dependency].append(task.qualified_name)
                task.update_dependency_state(dependency, self.scheduled_tasks_dict[dependency].state)
            else:
                routine, instance = dependency.split('.')
                instance = datetime.strptime(instance, config.dt_format_str)
                # Check for some record of the dependency
                task_records = self.state_manager.task_result(routine, instance)
                last_result = task_records.fetchone()
                if last_result is not None:
                    _, _, last_state, _ = last_result
                    task.update_dependency_state(dependency, last_state)
                else:
                    # Assume that if the dependency is meant to run in the future that it
                    # will be initialized at some point in the future.
                    if instance > reference_time:
                        self.task_dependencies[dependency] = [task.qualified_name]
                    else:
                        # The predecessor task will never run.  It didn't run in the past. And won't run
                        # in the future.  So what should happen? Should the downstream jobs run anyway or
                        # not? I take the view that dependencies are true dependencies and so don't run.
                        logger.debug('Cancelling %s, predecessor %s missing', task.qualified_name, dependency)
                        cancel = True
                        break
            logger.debug('Registered %s as dependent on %s', task.qualified_name, dependency)
        if cancel:
            task.update_state('Cancelled')

    def main_loop(self):
        overdue = True
        reference_time = datetime.today()
        while self.keep_running:
            logger.debug('Start new of loop')
            while overdue and self.keep_running:

                self.run_pending_jobs(reference_time)
                self.wait_for_updates()

                reference_time = datetime.today()
                if self.next_runtime() > reference_time:
                    logger.info('No tasks until: %s', self.next_runtime().strftime(config.dt_format_str))
                    overdue = False
            while not overdue and self.keep_running:
                # We need to check for updates since user instructions may still be sent at any time.
                # But that is infrequent so, we don't have to check constantly.
                # Therefore, we add a little buffer time in between checks. The bigger the buffer,
                # the lower the cycle usage, but the longer the potential lag when user input is sent.
                sleep_time = min(5, (self.next_runtime() - reference_time).total_seconds())
                time.sleep(sleep_time)
                self.wait_for_updates()

                reference_time = datetime.today()
                if self.next_runtime() <= reference_time:
                    logger.info('New tasks need to be run.')
                    overdue = True

    def run_pending_jobs(self, reference_time):
        next_runtime = self.next_runtime()
        if next_runtime <= reference_time:
            for task in self.scheduled_tasks_list:
                if task.time <= reference_time:
                    if task.state == 'Ready':
                        self.run_task(task)
                        self.run_pending_jobs(reference_time)
                else: # The list is ordered
                    break

    def run_task(self, task):
        logger.info('Running: %s', task.qualified_name)
        self.running_tasks.append(task.qualified_name)
        task.update_state('Running')
        task.start()
        self.schedule_next_task(self.registry.get_routine(task.name), task.time)

    def wait_for_updates(self):
        if not self.event_queue.empty():
            event = self.event_queue.get()
            if isinstance(event, Message):
                self.process_message(event)
            else:
                self.process_user_input(event)

    def process_message(self, message):
        self.state_manager.update(message.name, message.time, message.state)
        if message.qualified_name in self.task_dependencies:
            for down_stream_task_name in self.task_dependencies[message.qualified_name]:
                self.scheduled_tasks_dict[down_stream_task_name].update_dependency_state(message.qualified_name, message.state)
        if message.state in ['Success', 'Failure']:
            self.running_tasks.pop(self.running_tasks.index(message.qualified_name))
        if message.state in ['Success', 'Cancelled']:
            if message.state == 'Cancelled':
                self.schedule_next_task(self.registry.get_routine(message.name), message.time)
            self.remove_task(message.qualified_name)

    def process_user_input(self, instruction):
        if instruction == 'stop':
            self.shutdown()
        else:
            # Assume then, that this is an execute instruction and the argument is a qualified task name.
            logger.info('* Received Execute Instruction: %s', instruction)
            # TODO: What if the task doesn't exist here?
            task = self.scheduled_tasks_dict[instruction]
            if not task.state in ['Ready', 'Waiting']:
                # Task has been run and will need to be reset
                task = self.reset_task(task)
            self.run_task(task)

    def next_runtime(self):
        assert len(self.scheduled_tasks_dict) == len(self.scheduled_tasks_list)
        for task in self.scheduled_tasks_list:
            if task.state in ['Ready', 'Waiting']:
                return task.time

    def remove_task(self, qualified_name):
        logger.debug('Removing: %s', qualified_name)
        task = self.scheduled_tasks_dict[qualified_name]

        if qualified_name in self.task_dependencies:
            logger.debug('Removing %s from dependency map keys', qualified_name)
            del self.task_dependencies[qualified_name]

        for dependency in task.dependencies:
            if dependency in self.task_dependencies:
                if task.qualified_name in self.task_dependencies[dependency]:
                    logger.debug('Removing %s as dependent on %s', qualified_name, dependency)
                    self.task_dependencies[dependency].remove(task.qualified_name)

        logger.debug('Removing from both scheduled collections: %s', qualified_name)
        self.state_manager.update(task.name, task.time, 'Archived')
        self.scheduled_tasks_list.remove(task)
        del self.scheduled_tasks_dict[qualified_name]

    def reset_task(self, task):
        logger.info('Resetting: %s', task.qualified_name)
        new_task = Task(task.name, task.script, task.time, task.dependencies, queue=task.result_queue)
        self.scheduled_tasks_dict[task.qualified_name] = new_task
        self.scheduled_tasks_list.remove(task)
        bisect.insort(self.scheduled_tasks_list, new_task)
        return new_task

    def shutdown(self):
        logger.info('* Received shutdown instruction *')

        # Record the shutdown time, so jobs can be resumed on launch
        shutdown_time = datetime.today().strftime(config.dt_format_str)
        self.config.set('DEFAULT', 'Last_Shutdown', shutdown_time)
        with open(self.config.get('DEFAULT', 'config_path'), 'w') as config_file:
            self.config.write(config_file)
        logger.info('Recording shutdown time: %s', shutdown_time)

        number_running_tasks = len(self.running_tasks)
        logger.info('%s tasks still running.', number_running_tasks)
        if number_running_tasks != 0:
            for running_task in self.running_tasks:
                logger.info(running_task)
        while number_running_tasks != 0:
            self.wait_for_updates()
            number_running_tasks = len(self.running_tasks)
            if number_running_tasks == 0:
                logger.info('Outstanding tasks have finished running.')
        logger.info('* Shutdown completed normally *')
        self.keep_running = False




