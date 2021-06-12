import requests
import json
import boto3
import os
import sys
import getopt
import traceback
import utils.helper as Helper
import utils.logger as Logger
import utils.constants as Const
from datetime import datetime
from models.instance import Instance
from models.snapshot import SnapshotRequest
from freshtasks.api import Api
from freshtasks.task_utils import TaskUtils

#TODO("Catch FreshTasks Exceptions")

######################################
########## Global Variables ##########
######################################
logger = None
error = None


######################################
############ My Functions ############
######################################
def retrieve_arguments(argv):

    ticket = None

    # Try to get values from option arguments
    opts, _ = getopt.getopt(argv, "ht:", ["ticket="])

    # If no options passed, raise an error
    if len(opts) < 1:
        raise getopt.GetoptError(Const.EXCEPTION_OPTIONS_WRONG_ARGUMENTS)

    # Iterate though each options
    for opt, arg in opts:

        # If option help asked
        if opt == '-h':
            print(Const.EXCEPTION_OPTIONS_HELP)
            sys.exit()
        # If option ticket passed
        elif opt in ("-t", "--ticket"):
            ticket = arg

    # Both tickets and agent should be set
    # If one of them is missing, raise an error
    if ticket == None or ticket == "":
        raise getopt.GetoptError(Const.EXCEPTION_OPTIONS_MISSING_ARGUMENTS)

    return ticket

def logger_config():
    # Call the global logger variable
    global logger

    # log folder path
    LOG_FOLDER = os.path.join(os.path.dirname(__file__), "logs/")

    # create log folder
    if os.path.exists(LOG_FOLDER) is False:
        os.mkdir(LOG_FOLDER)

    # Assign to logger variable
    logger = Logger.create_logger(
        (LOG_FOLDER + datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + ".log")
    )

def load_open_tasks(ticket):
    # Make API call to Fresh Tasks
    api = Api(
        os.environ['ENV_FRESH_SERVICE_KEY_API_B64'], 
        os.environ["ENV_VALUE_DOMAIN_FRESHSERVICE_CKO"]
    )

    # Get the list of tasks
    tasks = api.load_tasks(ticket)

    # Get Open tasks only
    task_utils = TaskUtils(tasks).get_open()
    
    return task_utils

def filter_host_ips(tasks):
    # Retrieve valid ip address from tasks
    host_ip_addresses = Helper.retrieve_hosts(tasks)

    # Check if ip list is not empty
    if not host_ip_addresses:
        raise IndexError(Const.EXCEPTION_SNAPSHOT_UNDEFINED)

    return host_ip_addresses

def create_ec2_client():

    # Instantiate BOTO client for EC2
    ec2 = boto3.client('ec2')

    # Return the client
    return ec2

def query_instance(client, filters):

    # Filter instances
    response = client.describe_instances(Filters=filters)

    # Retrieve instances
    for r in response['Reservations']:

        for i in r['Instances']:

            return Instance.load(i)

    # Raise exception if an instance not found
    raise Exception(Const.EXCEPTION_NOT_FOUND_INSTANCE.format(
        filters[0]['Values'][0]))

def create_snapshots(client, snapshot_requests):

    # Initialize empty list of results strings and ids list
    ids = []
    messages = []

    # Iterate through each snapshot requests
    for sr in snapshot_requests:

        # Create a tag for each snapshot
        # Tag should consist of Name with the format: TodaysDate_ServerName_Snapshot
        tags = Const.require_tags_template(
            f"{Helper.format_today()}_{sr.hostname}_snapshot", sr.agent, sr.ticket_number)

        # Create the snapshot
        response = client.create_snapshot(
            Description=Const.DESC_SNAPSHOT.format(sr.hostname),
            VolumeId=sr.volume_id,
            TagSpecifications=Const.require_tags_spec_template(tags)
        )

        # Log the message
        log(Const.MESSAGE_SNAPSHOT_CREATED.format(
            sr.hostname, response['SnapshotId']))

        # Add id to list
        ids.append(response['SnapshotId'])

        # Create message and add to list
        messages.append(Const.MESSAGE_SNAPSHOT_CREATED.format(
            sr.hostname, response['SnapshotId']))

    # Return snapshot ids
    return ids, messages

def wait_for_snapshots_completion(client, snapshots_ids):

    waiter = client.get_waiter('snapshot_completed')

    waiter.wait(
        SnapshotIds = snapshots_ids,
        WaiterConfig={
            'Delay': 15,
            'MaxAttempts': 40
        }
    )

def post_to_slack(message, blocks=None):

    # Make API Call to Slack API
    response = requests.post('https://slack.com/api/chat.postMessage', {
        'token': os.environ["ENV_SLACK_KEY_API"],
        'channel': os.environ["ENV_SLACK_CHANNEL"],
        'text': message,
        'icon_url': "",
        'username': os.environ["ENV_SLACK_USERNAME"],
        'blocks': json.dumps(blocks) if blocks else None
    }).json()

    # Check if messages posted successfully
    if response['ok'] != True:
        raise Exception(Const.EXCEPTION_MESSAGE_ERROR_SLACK)

def log(message):
    # Logs an info message
    logger.info(message)

def debug(message):
    # Logs a debug message
    logger.debug(message)


#####################################
########### Main Function ###########
#####################################

def main(argv):
    # Call the global variables
    global logger, error

    # Try except clause to
    # handle all possible errors in the whole script
    # to prevent crash
    try:
        # Initiate Logger
        logger_config()

        # Retrieve ticket number
        # from command line option arguments
        ticket = retrieve_arguments(argv)

        # Retrive Username as Agent
        agent = Helper.get_username()        

        # Uncomment only for fast debugging purposes
        # ticket = os.environ['ENV_APP_TICKET']
        # agent = os.environ['ENV_APP_AGENT']

        # Log user execution
        log(Const.MESSAGE_USER_SCRIPT_LAUNCH.format(agent))

        # Get the list of tasks from FreshService
        tasks = load_open_tasks(ticket)

        # Retrieve valid host ips from tasks
        host_ip_addresses = filter_host_ips(tasks)

        # Define empty list of snapshot request
        snapshot_requests = []

        # Get EC2 client
        client = create_ec2_client()

        # For each IP address defined
        for ip in host_ip_addresses:

            # Define filters for EC2 client
            filters = [Const.require_filter_template(ip)]

            # Call the ec2 client
            instance = query_instance(client, filters)

            # Get the volume id of the instance
            volume_id = instance.root_volume_id

            # If instance has a root volume
            if volume_id != None:

                # Build snapshot request and
                # insert in request list
                s_request = SnapshotRequest(volume_id, instance.name, agent, ticket)
                snapshot_requests.append(s_request)

        # Filter duplicate snapshots and remove them
        snapshot_requests = Helper.remove_duplicate_snapshots(snapshot_requests)

        # Create snapshots
        snap_ids, results = create_snapshots(client, snapshot_requests)

        # Notify on Slack
        post_to_slack(Helper.construct_results_message(results, Const.MESSAGE_SNAPSHOT_NEW.format(ticket)))
        
        # Wait for Snapshot creation to be completed
        wait_for_snapshots_completion(client, snap_ids)

        # Notify on Slack
        post_to_slack(Const.MESSAGE_SNAPSHOT_COMPLETED.format(ticket))

    # Defin all possible exceptions as explicit as possible
    # The last one should always be 'Exception' clause to handle
    # unknown exceptions
    except getopt.GetoptError as GE:
        error = Const.EXCEPTION_OPTIONS_GENERAL.format(GE)
        log(error)
        debug(traceback.format_exc())
        sys.exit(2)

    except requests.exceptions.Timeout as TE:
        error = Const.EXCEPTION_TIMEOUT.format(TE)
        debug(error)
        debug(traceback.format_exc())

    except requests.exceptions.HTTPError as HE:
        error = Const.EXCEPTION_HTTP_ERROR.format(HE)
        debug(error)
        debug(traceback.format_exc())

    except Exception as e:
        error = Const.EXCEPTION_GENERAL.format(e)
        debug(error)
        debug(traceback.format_exc())

    # A separate try except to post message to slack
    try:
        if error != None:
            post_to_slack(Helper.construct_results_message([error], Const.MESSAGE_SNAPSHOT_CANCELLED.format(ticket)))
    except Exception as e:
        error = Const.EXCEPTION_GENERAL.format(e)
        debug(error)
        debug(traceback.format_exc())


if __name__ == "__main__":
    main(sys.argv[1:])
