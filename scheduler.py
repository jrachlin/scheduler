import os
import logging
import argparse
import threading
from datetime import datetime

# Internal imports
import input
import config
from core.registry import Registry
from core.state_manager import StateManager
from task_manager import TaskManager


logger = logging.getLogger(__name__)


def start_func(args):

    # Load the configuration file
    if args.mode == 'test':
        config_file = os.path.join(config.get_test_directory(), 'config.cfg')
    else:
        config_file = args.config_file
    configuration = config.load_config_file(config_file)

    # Setup logging
    log_mode = 'a' if args.resume else 'w'
    config.setup_logging(args.scheduler_name, args.log_level, log_mode)
    logger.info('<< Starting Program >>')

    # Record instance
    logger.debug('Create Instance File')
    config.create_instance(args.scheduler_name, config_file)

    # If there is an error in the program, then we need to clean up the instance file
    # before exiting. So, use a try / finally once the instance is created.
    try:
        # Load registry
        registry_file_path = configuration.get('DEFAULT', 'registry')
        registry = Registry(registry_file_path)

        # Load state data
        database_path = configuration.get('DEFAULT', 'database')
        state_manager = StateManager(database_path, args.wipe)

        # Setup the UI listener
        server, port = input.initialize_ui_listener()

        # Record the lister port
        configuration['SESSION']['port'] = str(port)
        with open(configuration.get('DEFAULT', 'config_path'), 'w') as config_file:
            configuration.write(config_file)

        # Launch UI listener
        ui_thread = threading.Thread(target=input.launch_ui_listener, args=(server,), daemon=True)
        ui_thread.start()
        event_queue = input.message_queue
        logger.info('<< Initial Setup Complete >>')

        # Initialize the Task Manager
        logger.info('<< Launching Task Manager >>')
        task_manager = TaskManager(event_queue, state_manager, registry, configuration)
        task_manager.launch(args.resume)

    finally:
        logger.debug('Clean Up Instance File')
        config.remove_instance(args.scheduler_name)


def status_func(args):
    configuration = config.load_config_file(config.get_instance_config_location(args.scheduler_name))
    state_manager = StateManager(configuration.get('DEFAULT', 'database'))
    results_list = []
    max_length = [0, 0, 0, 0]
    for row in state_manager.get_current_status(args.routine_name):
        results_list.append(row)
        for i in range(4):
            #if i in [1,3]:
            #    this_length = len(str(row[i]))
            #else:
            #    this_length = len(row[i])
            max_length[i] = max(max_length[i], len(str(row[i])))

    header = [value.ljust(length) for value, length in zip(['Name', 'Instance', 'Status', 'TimeStamp'], max_length)]
    header = '|' + '|'.join(header)
    print('-' * len(header))
    print(header)
    print('-' * len(header))

    for row in results_list:
        row = [str(value).ljust(length) for value, length in zip(row, max_length)]
        print('|' + '|'.join(row))


def execute_func(args):
    configuration = config.load_config_file(config.get_instance_config_location(args.scheduler_name))
    state_manager = StateManager(configuration.get('DEFAULT', 'database'))

    routine, instance = args.task_name.split('.')
    instance = datetime.strptime(instance, config.dt_format_str)

    task_info = state_manager.task_result(routine, instance)
    last_result = task_info.fetchone()
    if last_result is None:
        logger.error('Could not find %s. Check input.', args.task_name)

    input.send_user_input(args.task_name, configuration.getint('SESSION', 'port'))


def end_func(args):
    configuration = config.load_config_file(config.get_instance_config_location(args.scheduler_name))
    input.send_user_input('stop', configuration.getint('SESSION', 'port'))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Interface for schedule program.')

    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # Parser for Start Instruction
    start_parser = subparsers.add_parser('start', help='launch help')
    start_parser.add_argument('--scheduler_name', required=True, help='scheduler name')
    start_parser.add_argument('--config_file', help='Path of the config file')
    start_parser.add_argument('--log_level', default='INFO', help='Log Level')
    start_parser.add_argument('--mode', default='test', help='Run mode (test / prod)')
    start_parser.add_argument('--resume', action='store_true', help='Resume running from last shutdown')
    start_parser.add_argument('--wipe', action='store_true', help='Wipe database before starting')
    start_parser.set_defaults(func=start_func)

    # Parser for Stop Instruction
    stop_parser = subparsers.add_parser('stop', help='end help')
    stop_parser.add_argument('--scheduler_name', required=True, help='scheduler name')
    stop_parser.add_argument('--log_level', default='INFO', help='Log Level')
    stop_parser.set_defaults(func=end_func)

    # Parser for Status Instruction
    status_parser = subparsers.add_parser('status', help='status help')
    status_parser.add_argument('--scheduler_name', required=True, help='scheduler name')
    status_parser.add_argument('--routine_name', help='Check status of specific routine.')
    status_parser.add_argument('--log_level', default='INFO', help='Log Level')
    status_parser.set_defaults(func=status_func)

    # Parser for Execute Instruction
    execute_parser = subparsers.add_parser('execute', help='execute help')
    execute_parser.add_argument('--scheduler_name', required=True, help='scheduler name')
    execute_parser.add_argument('--task_name', help='Execute specific task: [Routine].[Date]T[Time]')
    execute_parser.add_argument('--log_level', default='INFO', help='Log Level')
    execute_parser.set_defaults(func=execute_func)

    args = parser.parse_args()
    args.func(args)
