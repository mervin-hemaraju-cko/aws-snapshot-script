import pytest
import requests
import main as Main

###############################
####### Important Note ########
###############################
## Tests should be performed ##
## in Playground Environment ##
###############################
###############################

class TestHelper:

    def test_post_to_slack(self):
        # Arrange
        message = "This is a message\n With new lines"

        # Act
        try:
            Main.post_to_slack(message)
            result = True
        except:
            result = False
            
        # Assert
        assert result == True

    def test_get_tasks_size(self):
        # Arrange
        ticket = "7303"
        expected_result = 2

        # Act
        result = Main.load_tasks(ticket)

        # Assert
        assert expected_result == len(result)

    def test_get_tasks_error(self):
        # Arrange
        ticket = "asdasd"
        expected_result = "An HTTP error occured while fetching tickets from FreshService"

        # Act
        try:
            Main.load_tasks(ticket)
            result = "Failed"
        except requests.exceptions.HTTPError as e:
            result = str(e)
            pass

        # Assert
        assert expected_result == result

    def test_get_tasks_empty(self):
        # Arrange
        ticket = "72"
        expected_result = "You don't have any tasks for snapshots"

        # Act
        try:
            Main.load_tasks(ticket)
            result = "Failed"
        except requests.exceptions.HTTPError as e:
            result = str(e)
            pass

        # Assert
        assert expected_result == result

    def test_query_instance_existing(self):

        # Arrange
        filters = [{
                'Name': 'private-ip-address',
                'Values': ["172.31.255.20"],
            }]

        expected_volume_id = "vol-0ab3909a5663e3a0c"
        expected_volume_name = "/dev/sda1"

        # Act
        client = Main.create_ec2_client()
        result = Main.query_instance(client, filters)

        # Assert
        assert expected_volume_id == result.root_volume_id
        assert expected_volume_name == result.root_volume_name

    def test_query_instance_nonexisting(self):

        # Arrange
        filters = [{
                'Name': 'private-ip-address',
                'Values': ["10.10.10.10"],
            }]

        expected_result = "No instance found for the IP address 10.10.10.10"

        # Act
        try:
            client = Main.create_ec2_client()
            result = Main.query_instance(client, filters)
        except Exception as e:
            result = str(e)
            
        # Assert
        assert expected_result == result

    def test_query_instance_tag_name_1Of2(self):

        # Arrange
        filters = [{
                'Name': 'private-ip-address',
                'Values': ["172.31.255.20"],
            }]

        expected_result = "win_jump_pub_01"

        # Act
        client = Main.create_ec2_client()
        result = Main.query_instance(client, filters).name

        # Assert
        assert result == expected_result

    def test_query_instance_tag_name_2Of2(self):

        # Arrange
        filters = [{
                'Name': 'private-ip-address',
                'Values': ["172.31.255.30"],
            }]

        expected_result = "lin_jump_pub_01"

        # Act
        client = Main.create_ec2_client()
        result = Main.query_instance(client, filters).name

        # Assert
        assert result == expected_result