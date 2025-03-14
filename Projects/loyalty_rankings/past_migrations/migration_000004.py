import os
import glob
import shutil
import re

def setup_log_directory():
    """
    Creates a log directory if it doesn't exist,
    moves the headshot_migration.log file into it,
    and renames it to the next sequential migration_XXXXXX.log file.
    """
    # Current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the log directory
    log_dir = os.path.join(current_dir, "logs")

    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"Created log directory: {log_dir}")
    else:
        print(f"Log directory already exists: {log_dir}")

    # Path to the source log file
    source_log = os.path.join(current_dir, "headshot_migration.log")

    # Check if the source log file exists
    if not os.path.exists(source_log):
        print(f"Source log file not found: {source_log}")
        return

    # Find the highest migration log number
    log_files = glob.glob(os.path.join(log_dir, "migration_*.log"))

    highest_number = 0
    for log_file in log_files:
        match = re.search(r'migration_(\d+)\.log', os.path.basename(log_file))
        if match:
            number = int(match.group(1))
            highest_number = max(highest_number, number)

    # Calculate the next log number
    next_number = highest_number + 1

    # Format the new log filename
    new_log_filename = f"migration_{str(next_number).zfill(6)}.log"
    destination_log = os.path.join(log_dir, new_log_filename)

    # Move and rename the log file
    shutil.move(source_log, destination_log)
    print(f"Moved and renamed log file to: {destination_log}")

setup_log_directory()
