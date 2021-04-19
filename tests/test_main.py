import pytest
import requests
import main as Main


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
        expected_result = 3

        # Act
        result = Main.load_tasks()

        # Assert
        assert expected_result == len(result)

    def test_get_tasks_error(self):
        # Arrange
        expected_result = "An HTTP error occured while fetching tickets from FreshService"

        # Act
        try:
            Main.ticket = "asdasd" # Change ticket to something unknown
            Main.load_tasks()
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
                'Values': ["172.31.1.94"],
            }]

        expected_volume_id = "vol-0a1f5b2643560d242"
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