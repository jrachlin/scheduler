import os
import logging
from configparser import ConfigParser

logger = logging.getLogger(__name__)
dt_format_str = '%Y-%m-%dT%H:%M:%S'
project_path = os.path.dirname(os.path.abspath(__file__))
scheduler_config = None

# Functions related to testing
def get_test_directory():
    return os.path.join(project_path, 'testing')

"""
Functions related to scheduler instance management

Launching the scheduler program creates a running instance of the application based on the files contained in a 
specified directory.  In order allow separate application instances to run simultaneously, we need a means to avoid
collisions (two instances based on the same set of files) and route user instructions to the intended instance.  This is
done by saving a uniquely named config file for each launched instance into a specified directory.
"""

def _get_instance_full_path(instance_name):
    """Returns the standard file path for the configuration file of a running scheduler instance"""
    file_path = os.path.join(project_path, 'instance')
    instance_full_path = os.path.join(file_path, instance_name)
    return instance_full_path

def create_instance(name, config_file):
    instance_full_path = _get_instance_full_path(name)
    if os.path.exists(instance_full_path):
        raise Exception('Instance {} already exists!'.format(name))
    else:
        with open(instance_full_path, 'w') as instance:
            instance.write(config_file)

def remove_instance(name):
    instance_full_path = _get_instance_full_path(name)
    if not os.path.exists(instance_full_path):
        raise Exception('Instance {} does not exist!'.format(name))
    else:
        os.remove(instance_full_path)

def get_live_instances():
    live_instances = []
    file_path = os.path.join(project_path, 'instance')
    for filename in os.listdir(file_path):
        instance_full_path = _get_instance_full_path(filename)
        with open(instance_full_path, 'r') as instance:
            config_file = instance.read()
        live_instances.append((filename, config_file))
    return live_instances

def get_instance_config_location(name):
    instance_full_path = _get_instance_full_path(name)
    with open(instance_full_path, 'r') as instance:
        config_path = instance.read()
    return config_path

def load_config_file(config_file):
    logger.info('Loading Configuration File: %s', config_file)

    global scheduler_config
    scheduler_config = ConfigParser()
    scheduler_config.read(config_file)
    scheduler_config.set('DEFAULT', 'root_directory', os.path.dirname(config_file))

    # Verify the registry file exists
    registry_file = scheduler_config.get('DEFAULT', 'registry')
    if not os.path.exists(registry_file):
        raise Exception('Registry does not exist!: {}'.format(registry_file))

    # Create a log directory as needed
    log_directory = scheduler_config.get('DEFAULT', 'log_directory')
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    return scheduler_config

def get_config_file():
    return scheduler_config

def setup_logging(filename, log_level, mode):
    log_directory = scheduler_config.get('DEFAULT', 'log_directory')
    log_file_name = os.path.join(log_directory, '{}.log'.format(filename))
    logging.basicConfig(filename=log_file_name, filemode=mode, level=log_level,
                        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt=dt_format_str)
