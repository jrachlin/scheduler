# scheduler
A cron-like task scheduler incorporating task-to-task dependencies.  This is a pure python task scheduler, meaning, that
any and all tasks managed by this program are ultimately in the form of an executable python file.

## QUICK USE
### Launch new scheduler
1. Create a folder to house the scheduler data: config files and log files
2. Ensure the following files are included in the new folder.  It will likely be easiest to make a copy of the
   sample files housed here: ~\scheduler\statics\
    * sample_registry.xml.  Rename to registry.xml and add your tasks.
    * sample_config.cfg. Rename to config.cfg, no changes needed.
3. Open a command prompt and navigate to the scheduler library directory
    * cd ~\scheduler
4. Launch in the following ways:
    * As a daemon process: start scheduler.py start --scheduler_name [NAME] --config_file [PATH] --mode prod
    * Within this window: python scheduler.py start --scheduler_name [NAME] --config_file [PATH] --mode prod

### Launching existing scheduler
start scheduler.py start --scheduler_name [NAME] --config_file [PATH] --mode prod

### End running scheduler
1. Open a command prompt and navigate to the scheduler library directory
    * cd ~\scheduler
2. python scheduler.py stop --scheduler_name [NAME]

### Review Task Status
1. Open a command prompt and navigate to the scheduler library directory
    * cd ~\scheduler
2. Execute status command per examples below
    * All: python scheduler.py status --scheduler_name [NAME]
    * By Routine: python scheduler.py status --scheduler_name [NAME] --routine_name testJob0
   
## PROGRAM STRUCTURE
scheduler.py: Command Line Interface

    * Instructions: Start, Stop, Status, Execute, Cancel

instance/:
    Each running instance of the scheduler program is represented by a correspondingly named file
    in this folder.  It prevents new instances of the same scheduler to be run simultaneously and
    allows the command line program to determine what port each running scheduler is listening to.


## OBJECT MODEL
Routine: An object representing a recurring task.  Each instance has a name, a script to run, a schedule to adhere to,
and a set of routines it depends on (that is, they must complete before this Routine can run) and set of Routines that
depend on it (that is, they are waiting for this Routine to finish before running).

Task: This is effectively an instance of a Routine.  Where a Routine has a schedule, a task is a specific instance.
For example, if you have a Routine that has a monthly schedule, an example of a Task would be the October instance of
that Routine.

Registry: The registry object is a dictionary of all the Routines.
