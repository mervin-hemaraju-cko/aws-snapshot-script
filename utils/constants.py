###############################################################
############## All constants values resides here ##############
###############################################################

# VALUES
VALUE_URL_BASE_FRESH_SERVICE_NOTES = "https://{}/api/v2/{}/{}/notes"

# MESSAGE
MESSAGE_SNAPSHOT_LAUNCHED = "The Snapshot Lambda has been started for {}"
MESSAGE_SNAPSHOT_CREATED = "The snapshot for {} has been created under {}"
MESSAGE_SNAPSHOT_NEW_SLACK = "Snapshots have been created for {}:\n"
MESSAGE_SNAPSHOT_NEW_FSNOTE = "<div>Snapshot request started for the below IDs: </div><br/>"
MESSAGE_SNAPSHOT_COMPLETED = "Snapshot creation completed for ticket {}"
MESSAGE_SNAPSHOT_CANCELLED = "Request for ticket {} has been cancelled due to the following errors:\n"
MESSAGE_USER_SCRIPT_LAUNCH = "The user {} has executed the script."

# Descriptions
DESC_SNAPSHOT = "This is a snapshot for server {}"

# Exceptions
EXCEPTION_NOT_FOUND_INSTANCE = "No instance found for the IP address {}"
EXCEPTION_TIMEOUT = "Request timeout occured: {}"
EXCEPTION_HTTP_ERROR = "HTTP error occured: {}"
EXCEPTION_GENERAL = "An unexpected error occurred: {}"
EXCEPTION_MESSAGE_ERROR_SLACK = "Message could not be posted to Slack channel"
EXCEPTION_MESSAGE_ERROR_FRESHSERVICE_NOTE = "Your Fresh Service note couldn't be posted."
EXCEPTION_OPTIONS_GENERAL = "{}. Use option -h for help"
EXCEPTION_OPTIONS_MISSING_ARGUMENTS = "Missing arguments"
EXCEPTION_OPTIONS_WRONG_ARGUMENTS = "Wrong arguments passed"
EXCEPTION_OPTIONS_HELP = "Options available: -t <ticket>"
EXCEPTION_TASKS_EMPTY = "You don't have any tasks for snapshots"
EXCEPTION_NON_USER_EXECUTION = "Please run this script in a non-root user."
EXCEPTION_SNAPSHOT_UNDEFINED = "No snapshots defined for this ticket. Please verify the format again."

# Dictionary values

# List of possible ticket ops
ticket_dict = {
        "#SR" : "tickets",
        "#INC": "tickets",
        "#CHN": "changes",
        "#PRB": "problems"
    }

def require_filter_template_ip(ip_address):
    return {
        'Name': 'private-ip-address',
        'Values': [ip_address],
    }

def require_filter_template_hostname(hostname):
    return {
        'Name': 'tag:Name',
        'Values': [hostname],
    }
    
def require_headers_template(api_key):
    return {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {api_key}"
    }


def require_tags_template(name, agent, ticket):
    return [
        {
            "Key": "Name",
            "Value": name
        },
        {
            "Key": "CreatorName",
            "Value": agent
        },
        {
            "Key": "Ticket",
            "Value": ticket
        }
    ]


def require_tags_spec_template(tags):
    return [
        {
            'ResourceType': 'snapshot',
            'Tags': tags
        },
    ]

def require_payload_fs_note(message):
    return {
        "body": message
    }