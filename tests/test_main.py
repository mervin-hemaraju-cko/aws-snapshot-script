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

    # Uncomment this test for the Slack posting
    # def test_post_to_slack(self):
    #     # Arrange
    #     message = "This is a message\n With new lines"

    #     # Act
    #     try:
    #         Main.post_to_slack(message)
    #         result = True
    #     except:
    #         result = False
            
    #     # Assert
    #     assert result == True

    def test_get_tasks_NormalData(self):
        # Arrange
        ticket = "#CHN-7303"
        expected_result = 3

        # Act
        result = Main.load_open_tasks(ticket)

        # Assert
        assert expected_result == len(result)

    def test_get_tasks_AbnormalData(self):
        # Arrange
        ticket = "asdasd"
        expected_result = "Incorrect ticket format provided. Please read the docs"

        # Act
        try:
            Main.load_open_tasks(ticket)
            result = "Failed"
        except IndexError as e:
            result = str(e)
            pass

        # Assert
        assert expected_result == result

    def test_get_tasks_EmptyData(self):
        # Arrange
        ticket = "#CHN-72"
        expected_result = []

        # Act
        result = Main.load_open_tasks(ticket)

        # Assert
        assert expected_result == result

    def test_filter_host_ip_NormalData(self):
        # Arrange
        ticket = "#CHN-7303"
        expected_size = 2

        # Act
        tasks = Main.load_open_tasks(ticket)
        result = Main.filter_host_ips(tasks)

        # Assert
        assert len(result) == expected_size

    def test_filter_host_ip_EmptyData(self):
        # Arrange
        ticket = "#CHN-72"
        expected_result = "No snapshots defined for this ticket. Please verify the format again."

        # Act
        try:
            tasks = Main.load_open_tasks(ticket)
            result = Main.filter_host_ips(tasks)
        except IndexError as e:
            result = str(e)
            pass

        # Assert
        assert expected_result == result

    def test_query_instance_NormalData(self):

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

    def test_query_instance_AbnormalData(self):

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