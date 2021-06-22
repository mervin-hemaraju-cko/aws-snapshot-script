import json, pytest, os
import main as Main
from freshtasks.api import Api
from freshtasks.task import Task

###############################
####### Important Note ########
###############################
## Tests should be performed ##
## in Playground Environment ##
###############################
###############################

class TestMain:

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

    def test_close_task_NormalData(self):
        # Arrange
        api = Api(
            os.environ['ENV_FRESH_SERVICE_KEY_API_B64'], 
            os.environ["ENV_VALUE_DOMAIN_FRESHSERVICE_CKO"]
        )
        ticket = "#CHN-1"
        tasks = []
        expected_result = True

        # Act
        try:
            # Load test file
            with open("tests/test_data/data_tasks_close.json") as json_out:

                for json_obj in json.load(json_out):
                    task = Task(json_obj)
                    tasks.append(task)

            Main.close_tasks(api, tasks, ticket)
            
            result = True
        except:
            result = False

        # Assert
        assert expected_result == result

    def test_add_note_on_ticket_NormalData(self):

        # Arrange
        ticket = "#CHN-1"
        message = "This is a message from python unit test"

        # Act
        Main.add_note_on_ticket(ticket, message)

        # Assert
        assert True
    
    def test_add_note_on_ticket_AbnormalData(self):

        # Arrange
        ticket = "#CHN-0"
        message = "This is a message from python unit test"
        expected_result = "Your Fresh Service note couldn't be posted."

        # Act
        try:
            Main.add_note_on_ticket(ticket, message)
            result = "FAILED"

        except Exception as e:
            result = str(e)

        # Assert
        assert expected_result == result


    testdata = [
        ("#CHN-1", 1),
        ("CHN-1", 1),
        ("#CHN-2", 0),
        ("CHN-2", 0),
    ]
    @pytest.mark.parametrize("ticket,expected_result", testdata)
    def test_get_tasks_NormalData(self,ticket, expected_result):

        # Act
        result, _ = Main.load_open_tasks(ticket)

        # Assert
        assert expected_result == len(result)

    testdata = [
        ("#CHN--1", "Incorrect ticket format provided. Please read the docs"),
        ("asdas", "Incorrect ticket format provided. Please read the docs"),
        ("CHN1", "Incorrect ticket format provided. Please read the docs"),
        ("123", "Incorrect ticket format provided. Please read the docs"),
    ]
    @pytest.mark.parametrize("ticket,expected_result", testdata)
    def test_get_tasks_AbnormalData(self, ticket, expected_result):
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
        ticket = "#CHN-2"
        expected_result = []

        # Act
        result, _ = Main.load_open_tasks(ticket)

        # Assert
        assert expected_result == result

    def test_filter_host_ip_NormalData(self):
        # Arrange
        ticket = "#CHN-1"
        expected_size = 2

        # Act
        tasks, _ = Main.load_open_tasks(ticket)

        result = Main.filter_host_ips(tasks)

        # Assert
        assert len(result) == expected_size

    def test_filter_host_ip_EmptyData(self):
        # Arrange
        ticket = "#CHN-2"
        expected_result = "No snapshots defined for this ticket. Please verify the format again."

        # Act
        try:
            tasks, _ = Main.load_open_tasks(ticket)
            result = Main.filter_host_ips(tasks)
        except IndexError as e:
            result = str(e)
            pass

        # Assert
        assert expected_result == result

    def test_query_instance_NormalData_ByIp_1Of2(self):

        # Arrange
        host = "172.31.255.20"

        expected_name = "win_jump_pub_01"
        expected_volume_id = "vol-0ab3909a5663e3a0c"
        expected_volume_name = "/dev/sda1"

        # Act
        client = Main.create_ec2_client()
        result = Main.query_instance(client, host)

        # Assert
        assert expected_name == result.name
        assert expected_volume_id == result.root_volume_id
        assert expected_volume_name == result.root_volume_name

    def test_query_instance_NormalData_ByIp_2Of2(self):

        # Arrange
        host = "172.31.255.30"

        expected_name = "lin_jump_pub_01"
        expected_volume_id = "vol-0430d0945194a0a59"
        expected_volume_name = "/dev/sda1"

        # Act
        client = Main.create_ec2_client()
        result = Main.query_instance(client, host)

        # Assert
        assert expected_name == result.name
        assert expected_volume_id == result.root_volume_id
        assert expected_volume_name == result.root_volume_name

    def test_query_instance_NormalData_ByHostname_1Of2(self):

        # Arrange
        host = "win_jump_pub_01"

        expected_name = "win_jump_pub_01"
        expected_volume_id = "vol-0ab3909a5663e3a0c"
        expected_volume_name = "/dev/sda1"

        # Act
        client = Main.create_ec2_client()
        result = Main.query_instance(client, host)

        # Assert
        assert expected_name == result.name
        assert expected_volume_id == result.root_volume_id
        assert expected_volume_name == result.root_volume_name

    def test_query_instance_NormalData_ByHostname_2Of2(self):

        # Arrange
        host = "lin_jump_pub_01"

        expected_name = "lin_jump_pub_01"
        expected_volume_id = "vol-0430d0945194a0a59"
        expected_volume_name = "/dev/sda1"

        # Act
        client = Main.create_ec2_client()
        result = Main.query_instance(client, host)

        # Assert
        assert expected_name == result.name
        assert expected_volume_id == result.root_volume_id
        assert expected_volume_name == result.root_volume_name

    def test_query_instance_AbnormalData1Of2(self):

        # Arrange        
        host = "10.10.10.10"
        expected_result = "No instance found for the IP address 10.10.10.10"

        # Act
        try:
            client = Main.create_ec2_client()
            result = Main.query_instance(client, host)
        except Exception as e:
            result = str(e)
            
        # Assert
        assert expected_result == result
    
    def test_query_instance_AbnormalData2Of2(self):

        # Arrange        
        host = "unknown"
        expected_result = "No instance found for the IP address unknown"

        # Act
        try:
            client = Main.create_ec2_client()
            result = Main.query_instance(client, host)
        except Exception as e:
            result = str(e)
            
        # Assert
        assert expected_result == result