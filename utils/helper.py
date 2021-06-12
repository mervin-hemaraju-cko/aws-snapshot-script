import getpass
from datetime import date
import utils.constants as Const

# This function checks whether the task title
# is a valid approved snapshot to be done
# this can only be recognized by the words [snap] or [snapshot]
# Any other keywors would be considered not a snapshot
def retrieve_hosts(tasks):

    hosts = []

    for task in tasks:

        # Define a list of possible keywords
        keywords = ["snapshots", "snapshot"]

        # Check if title of task matches keyword
        if(task.title.lower().strip() in keywords):

            # Retrieve the description and strip
            description = task.description.strip()

            if(description != "" and description != None):
                # Split to get hosts
                desc_hosts = description.split(";")

                # Extend list in case there are multiple tasks with snapshots
                hosts.extend(desc_hosts)

    # Return list of hosts
    return hosts

# This function returns today's date
# in the following format YYYYMMDD
def format_today():
    today = date.today()
    return today.strftime("%Y%m%d")

# Message construct
# Construct a message with different lines
def construct_results_message(results, header):

    for result in results:
        header += f"{result}\n"

    return header

# Return the current username
# logged on the server
def get_username():
    username = getpass.getuser()

    if username == "root":
        raise Exception(Const.EXCEPTION_NON_USER_EXECUTION)

    return getpass.getuser()

# Remove duplicates in snapshot requests
def remove_duplicate_snapshots(snapshot_requests):
    new_list = []
    
    for request in snapshot_requests:
        is_present = any(x.volume_id == request.volume_id for x in new_list)

        if not is_present:
            new_list.append(request)
    
    return new_list