# AWS Snapshot Automation  


* [Overview](#overview)
* [Important Notes](#important-notes)
* [User Section](#user-section)
* [Admin Section](#admin-section)
    * [Dependencies](#dependencies)
    * [Environment Variables](#environment-variables)
* [Technical Section](#technical-section)
    * [Code Samples](#code-samples)
* [Troubleshooting](#troubleshooting)

<br/>

## Overview 
--------------------------------

To save time when taking snapshots on Amazon Web Services and also to reduce human error-prone, a script has been deployed to automate this task.

The link to the GitHub repo can be found [here](https://github.com/mervin-hemaraju-cko/aws-snapshot-script).

This document can be decoupled into 3 main parts:

* [The User Section](#user-section) (How to use the script)
    
* [The Admin Section](#admin-section) (How to deploy the script)
    
* [The Technical Section](#technical-section) (A peek inside the code)

<br/>

## Important Notes
----------------------------------------
<br/>

### What does the script do for you?

1.  The script can save you time especially when in need to perform snapshots on a list of servers.
    
2.  The script will tag the snapshots with the appropriate tags. (Creator, Name, Ticket)
    
3.  The script will notify you on Slack when the snapshot has started and been completed.
    
4.  The script will provide you the snapshot id(s) on Slack upon creation.
    
5.  The script only takes root volume snapshots.

6.  The script will close the Fresh Service task after successful completion.
    
<br/>

### What the script doesn’t do for you?

1.  The script **will not** delete the snapshots automatically. The user executing the snapshot request(s) will need to clean up the snapshot(s) if necessary after using them.
    
2.  The script will not take snapshots of non-root volumes.
    
<br/>

### Supported Tickets:

The currently supported ticket types are:

*   Change Requests (#CHN-XXXX)
    
*   Service Requests (#SR-XXXX)
    
*   Incidents (#INC-XXXX)
    
*   Problems (#PRB-XXXX)

<br/>  

## User Section
-----------------------

<br/>

### Instructions

There are a set of instructions to **strictly** follow to run the script correctly.

1.  The correct AWS profile needs to be switched to the desired environment before running the script.
    
2.  A list of tasks should be defined in Fresh Service in the following syntax (A screenshot has been inserted below):
    
    *   Only tasks with the title of **snapshot(s)** will be taken into considerations. In the description of the task, list all your instances either by **instance name** or **IP number** separated by a **semi-column**:
        
![Task Format](./screenshots/task_format.png)

```
In case the script fails for any sort of errors, NO snapshots will be taken. Snapshots are taken only if the script runs successfully. This has been done to alleviate confusion and duplications.
```

```
The script will not take **Closed** tasks into considerations.
```

```
You can take Change [#CHN-7303](https://checkoutsupport.freshservice.com/itil/changes/7303#tasks) as an example
```
<br/>

### Run the Script

Finally, you can run the script by going on the hosting server (where the script is hosted), navigating to the root folder of the script, and running the following command: `./run.sh`

```
Before running the script, you will need to set the variable **$TICKET** with your ticket number as such:
```

```
i.e. export TICKET=#CHN-1234

i.e. export TICKET=#SR-1234
```

<br/>

## Admin Section
-------------------------------------

This section guides you on installing and deploying the script in a production environment.

To be able to run the script on a server, you will need a combination of installed dependencies and environment variables pre-set.

<br/>

### Dependencies

To install the dependencies, run the following command in the root project directory:

`pip install -r requirements.txt`

<br/>

### Environment Variables

A set of environment variables is necessary to be initialized before running the script.

The list below can be written in a `.env` file and then use the command `source file.env` to export the environment variables.

```
export ENV_FRESH_SERVICE_KEY_API_B64=""

export ENV_SLACK_KEY_API=""
export ENV_SLACK_CHANNEL=""
export ENV_SLACK_USERNAME=""
```
```
No secret keys are defined for Boto3 as it will make use of the underlying profiles of AWS CLI to run on the desired AWS environment.
```
<br/>

## Technical Section
-------------------------

The script has been coded fully in Python Programming Language.

The dependencies below have been used in the script:

* [Boto3 (AWS Python SDK)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
    
* [FreshTask](https://github.com/mervin-hemaraju-cko/fresh-tasks) (My own intermediary API to FreshService)
    
* [Slack API](https://api.slack.com/)
    

When a user executes the script, the following actions are executed in order:

1. The target instances information are taken from FreshService tickets using the FreshTask package
    
2. Using the captured server information, they are processed in Boto which is the Python SDK for Amazon Web Services, which will return the matched instance.
    
3. The instance is then processed further to obtain its root volume ID.
    
4. The snapshots of the root volume IDs are taken.
    
5. A message is sent to Slack with a list of all snapshots IDs created using the Slack API.
    
6. After snapshots are completed, another message is sent to Slack notifying the completion.
    
<br/>

### Code Samples

Below are some core code samples:

<br/>

#### Query the instance from AWS using Boto3

```
def query_instance(client, filters):

    response = client.describe_instances(Filters=filters)

    for r in response['Reservations']:

        for i in r['Instances']:

            return Instance.load(i)

    raise Exception(Const.EXCEPTION_NOT_FOUND_INSTANCE.format(
        filters[0]['Values'][0]))
```
<br/>

#### Create snapshots using the Boto3 client

```
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
```

<br/>

#### Post messages to Slack using the Slack API

```
def post_to_slack(message, blocks=None):

    response = requests.post('https://slack.com/api/chat.postMessage', {
        'token': os.environ["ENV_SLACK_KEY_API"],
        'channel': os.environ["ENV_SLACK_CHANNEL"],
        'text': message,
        'icon_url': "",
        'username': os.environ["ENV_SLACK_USERNAME"],
        'blocks': json.dumps(blocks) if blocks else None
    }).json()

    if response['ok'] != True:
        raise Exception(Const.EXCEPTION_MESSAGE_ERROR_SLACK)
```
<br/>

## Troubleshooting
---------------------------

Some situations can cause the script to fail. It could be due to wrong input(data) or a lack of internet connectivity.

Below are some basic scenarios and their impact:

<br/>

### General Scenarios

* **The server has lost internet connection**
    
    * If the server running the script loses internet connection, a connection timeout will occur when trying to fetch the information from Fresh Service and the script will stop
        
* **Incorrect IP Address given**
    
    * At any point, if an incorrect IP address (not existing on the AWS environment) has been inserted through a task, the script will cancel all snapshot creations. This is so that confusion can be alleviated as to which snapshots have been created and which have not. A message will be sent to the Slack Channel informing you about the error.
        
* **Wrong ticket number provided**
    
    * If the wrong ticket doesn’t contain any syntax which will cause snapshots to be taken, the script will just stop with the result of no snapshot requests found.
        
    * If the wrong ticket does contain snapshot request syntax, snapshots will be taken for the given servers. **The user will then have to manually delete the snapshots on the AWS console.**

<br/>  

### Advanced troubleshooting

Sometimes, the error will not be as predictive of the error message given. To further troubleshoot an issue, each time the script is run, a set of log files is generated and stored in the `log` folder in the project's root folder.

```
Log files are created for each date and time the script is run and is in the following format:

2021-04-15 20:07:21,562 DEBUG retryhandler.py 187 No retry needed.
2021-04-15 20:07:21,562 DEBUG main.py 160 An unexpected error occurred: name 'agent' is not defined
2021-04-15 20:07:21,564 DEBUG connectionpool.py 971 Starting new HTTPS connection (1): slack.com:443
2021-04-15 20:07:22,035 DEBUG connectionpool.py 452 https://slack.com:443 "POST /api/chat.postMessage HTTP/1.1" 200 227
```