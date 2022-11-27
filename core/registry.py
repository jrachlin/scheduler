import os
import logging
import xml.etree.ElementTree as ET

from core.routine import Routine


logger = logging.getLogger(__name__)


class Registry:
    def __init__(self, xml_source):
        """
        Parse a registry xml file describing the desired Routines and their dependencies.
        Create all the Routine objects and store into a dictionary.

        Args:
            xml_source (str): File path to xml based registry file
        """
        if not os.path.isfile(xml_source):
            raise Exception('Could not find registry xml: {}'.format(xml_source))

        self.routines = {}
        logger.info('Loading Registry File: %s', xml_source)
        root = ET.parse(xml_source).getroot()

        # Create Routines
        for definition in root:
            logger.debug('Loading Routine: %s', definition.attrib.get('name'))
            self.add_routine(Routine(**definition.attrib))

        # Add Routine dependencies
        for definition in root:
            successor = definition.attrib.get('name')
            for dependency in definition.iter('dependency'):
                predecessor = dependency.attrib.get('name')
                logger.debug('Creating dependency: %s depends on %s', successor, predecessor)
                self.add_dependency(predecessor, successor)

        logger.info('Loading Registry File: Finished')

    def __iter__(self):
        return iter(self.routines.items())

    def get_routine(self, routine_name):
        """
        Retrieve routine object by name

        Args:
            routine_name (str): name of the routine object to return
        """
        return self.routines[routine_name]

    def add_routine(self, routine):
        """
        Add a routine object to the registry

        Args:
            routine (Routine): The routine object to add to the registry
        """
        new_routine_name = routine.name
        if self.routines.get(new_routine_name):
            raise Exception('Name conflict: %s already exists in registry.' % new_routine_name)
        self.routines[new_routine_name] = routine

    def add_dependency(self, predecessor_name, successor_name):
        """
        Register a dependency between two routines

        Args:
            predecessor_name (str): Name of upstream Routine
            successor_name (str): Name of downstream (dependent) Routine
        """
        self.routines[successor_name].depends_on(self.routines[predecessor_name])
