import os
import sqlite3
import logging
from datetime import datetime

import config


logger = logging.getLogger(__name__)


class StateManager:
    """
    Interface for sqlite database which houses the records of all task-level state transitions.
    """
    def __init__(self, database_path, clean_start=False):
        """
        Initialize object.
        :param database_path: File path to sqlite database file (existing or desired location)
        :param clean_start: If true, delete all existing records from the database before beginning.
        """
        self.database_path = database_path
        # If database doesn't exist, create it.
        if not os.path.exists(self.database_path):
            logger.info('Database does not exist, creating: %s', self.database_path)
            self.create_database()
        # Store database connection
        logger.info('Connecting to database: %s', self.database_path)
        self.database = sqlite3.connect(database_path, detect_types=sqlite3.PARSE_DECLTYPES)
        # Delete records from database, if requested
        if clean_start:
            logger.warning('Deleting existing database records.')
            self.delete_all_records()

    def create_database(self):
        """
        Create a new database file having a 'state' table which will be used to record task-level state transitions.
        """
        # Get 'state' table definition and create it
        setup_file = os.path.join(config.project_path, '../statics', 'state.sql')
        with sqlite3.connect(self.database_path) as conn:
            with open(setup_file) as setup_file:
                conn.executescript(setup_file.read())

    def delete_all_records(self):
        """
        Delete all records in the 'state' table.
        """
        with self.database as conn:
            conn.executescript('DELETE FROM state')

    def update(self, task_name, task_instance, state):
        """
        Record a new task-level state transition.
        :param str task_name: The name of the task (same as routine name)
        :param datetime task_instance: The task datetime, which distinguishes this task from others of the same routine
        :param str state: New task state ['Ready', 'Waiting', 'Failure', 'Success', 'Archived', 'Cancelled']
        """
        query = 'INSERT INTO state VALUES (?, ?, ?, ?)'
        timestamp = datetime.today()
        new_row = (task_name, task_instance, state) + (timestamp,)
        with self.database as conn:
            conn.execute(query, new_row)

    def get_current_status(self, routine_name=None):
        """
        Returns the last state for all non-Archived tasks.
        :param str routine_name: The name of the routine (optional, if you want to filter results)
        :return: iterable of tuples
        """
        query = """
                SELECT s.routine, s.instance, s.state, s.state_time_stamp
                FROM (
                    SELECT routine, instance, MAX(state_time_stamp) as last
                    FROM state
                    GROUP BY routine, instance
                ) m
                INNER JOIN state s
                ON s.routine = m.routine
                AND s.instance = m.instance
                AND s.state_time_stamp = m.last
                WHERE s.state in ('Waiting', 'Ready', 'Failure', 'Cancelled', 'Running')
                {}
                ORDER BY s.instance, s.state_time_stamp
                """
        name_filter = "AND s.routine == '{}'".format(routine_name) if routine_name else ''
        query = query.format(name_filter)
        with self.database as conn:
            results = conn.execute(query)
        return results

    def task_result(self, task_name, task_instance):
        """
        Returns all state information for a particular task
        :param str task_name: The name of the task (same as routine name)
        :param task_instance: The task datetime, which distinguishes this task from others of the same routine
        :return: iterable of tuples
        """
        query = """
                SELECT * FROM state
                WHERE routine = '{}'
                AND instance = '{}'
                AND state != 'Archived'
                ORDER BY state_time_stamp DESC
                """
        query = query.format(task_name, task_instance)
        with self.database as conn:
            results = conn.execute(query)
        return results

    def close(self):
        """
        Close the cached database connection.
        """
        logger.info('Closing database connection: %s', self.database_path)
        self.database.close()