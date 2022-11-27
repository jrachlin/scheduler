# scheduler
A cron-like task scheduler incorporating task-to-task dependencies

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

REGISTRY
    ROUTINES >> TASK (Can be thought of like an instance of routine)
        SCHEDULE (CRON)
        SCRIPT

TASK MANAGER
    TASKS