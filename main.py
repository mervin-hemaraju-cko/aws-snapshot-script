import requests
import json
import boto3.ec2
import os
import sys
import getopt
import utils.helper as Helper
import utils.logger as Logger
import utils.constants as Const
from datetime import datetime
from models.instance import Instance
from models.task import Task
from models.snapshot import SnapshotRequest

# DISCUSS ("Change tickets only or SR Tickets included")

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
    agent = None

    # Try to get values from option arguments
    opts, args = getopt.getopt(argv, "ht:a:", ["ticket=", "agent="])

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
        
        # If option agent passed
        elif opt in ("-a", "--agent"):
            agent = arg

    # Both tickets and agent should be set
    # If one of them is missing, raise an error
    if ticket == None or agent == None:
        raise getopt.GetoptError(Const.EXCEPTION_OPTIONS_MISSING_ARGUMENTS)

    return ticket, agent


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


def load_tasks(ticket):

    # Build headers for FreshService call
    headers = Const.require_headers_template(
        os.environ['ENV_FRESH_SERVICE_KEY_API_B64'])

    # Get tasks from API FreshService
    response = requests.get(Const.VALUE_URL_BASE_FRESH_SERVICE_TASKS.format(
        os.environ['ENV_FRESH_SERVICE_URL'], ticket), headers=headers)

    # Checks if GET call is successfull
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            Const.EXCEPTION_HTTP_ERROR_FRESHSERVICE)

    # Format and load tasks
    tasks = Task.loads(json.loads(response.content)["tasks"])

    # If tasks is empty, raise an exception
    if not tasks:
        raise requests.exceptions.HTTPError(Const.EXCEPTION_TASKS_EMPTY)

    # Return tasks
    return tasks


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

    # Initialize empty list of results strings
    results = []

    # Iterate through each snapshot requests
    for sr in snapshot_requests:

        # Create a tag for each snapshot
        # Tag should consist of Name with the format: TodaysDate_ServerName_Snapshot
        tags = Const.require_tags_template(
            f"{Helper.format_today()}_{sr.hostname}_snapshot", sr.agent)

        # Create the snapshot
        response = client.create_snapshot(
            Description=Const.DESC_SNAPSHOT.format(sr.hostname),
            VolumeId=sr.volume_id,
            TagSpecifications=Const.require_tags_spec_template(tags)
        )

        # Log the message
        log(Const.MESSAGE_SNAPSHOT_CREATED.format(
            sr.hostname, response['SnapshotId']))

        # Add message to results
        results.append(Const.MESSAGE_SNAPSHOT_CREATED.format(
            sr.hostname, response['SnapshotId']))

    # Return results
    return results


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
    # Uncomment only for fast debugging purposes
    # ticket = os.environ['ENV_APP_TICKET']
    # agent = os.environ['ENV_APP_AGENT']

    # Try except clause to
    # handle all possible errors in the whole script
    # to prevent crash
    try:
        # Initiate Logger
        logger_config()

        # Retrieve ticket number and agent
        # from command line option arguments
        ticket, agent = retrieve_arguments(argv)

        # Get the list of tasks from FreshService
        tasks = load_tasks(ticket)

        # Define empty list of snapshot request
        snapshot_requests = []

        # Get EC2 client
        client = create_ec2_client()

        # For each IP address defined
        for task in tasks:

            # Define filters for EC2 client
            filters = [Const.require_filter_template(task.hostip)]

            # Call the ec2 client
            instance = query_instance(client, filters)

            # Get the volume id of the instance
            volume_id = instance.root_volume_id

            # If instance has a root volume
            if volume_id != None:
                # Build snapshot request and
                # insert in request list
                s_request = SnapshotRequest(volume_id, task.hostname, agent)
                snapshot_requests.append(s_request)

        # Create snapshots
        results = create_snapshots(client, snapshot_requests)

        # Post messages to Slack
        post_to_slack(Helper.construct_results_message(results, ticket))

    # Defin all possible exceptions as explicit as possible
    # The last one should always be 'Exception' clause to handle
    # unknown exceptions
    except getopt.GetoptError as GE:
        print(Const.EXCEPTION_OPTIONS_GENERAL.format(GE))
        sys.exit(2)

    except requests.exceptions.Timeout as TE:
        error = Const.EXCEPTION_TIMEOUT.format(TE)
        debug(error)

    except requests.exceptions.HTTPError as HE:
        error = Const.EXCEPTION_HTTP_ERROR.format(HE)
        debug(error)

    except Exception as e:
        error = Const.EXCEPTION_GENERAL.format(e)
        debug(error)

    # A separate try except to post message to slack
    try:
        if error != None:
            post_to_slack(Helper.construct_results_message([error], ticket))
    except Exception as e:
        error = Const.EXCEPTION_GENERAL.format(e)
        debug(error)


if __name__ == "__main__":
    main(sys.argv[1:])