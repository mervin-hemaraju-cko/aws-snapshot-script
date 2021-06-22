import pytest
import json
import utils.helper as Helper
from models.snapshot import SnapshotRequest
from freshtasks.task import Task

class TestHelper:

    testdata = [
        ("tests/test_data/data_tasks_normald.json", ["1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4"]),
        ("tests/test_data/data_tasks_mixd.json", ["10.20.20.20", "10.30.30.30"]),
        ("tests/test_data/data_tasks_abnormald.json", [])
    ]
    @pytest.mark.parametrize("test_data,expected_result", testdata)
    def test_retrieve_hosts(self,test_data,expected_result):

        # Arrange
        tasks = []

        # Act
        # Load test file
        with open(test_data) as json_out:

            for json_obj in json.load(json_out):
                task = Task(json_obj)
                tasks.append(task)

        result = Helper.retrieve_hosts(tasks)

        # Assert
        assert result == expected_result

    testdata = [
        (["ms1", "ms2", "ms3"],'''Your message is: ms1\nms2\nms3\n'''),
        (["this is a ms1"],'''Your message is: this is a ms1\n'''),
        (["ms4", "ms5"],'''Your message is: ms4\nms5\n'''),
        ([],'''Your message is: '''),
    ]
    @pytest.mark.parametrize("test_data,expected_result", testdata)
    def test_construct_results_message(self,test_data,expected_result):
        # Arrange
        header = "Your message is: "

        # Act
        result = Helper.construct_results_message(test_data, header)

        # Assert
        assert result == expected_result

    def test_format_today(self):
        # Arrange
        expected_result = "20210622"

        # Act
        result = Helper.format_today()

        # Assert
        assert expected_result == result

    def test_get_username(self):
        # Arrange
        expected_result = "th3pl4gu3"

        # Act
        result = Helper.get_username()

        # Assert
        assert result == expected_result

    testdata = [
        ([
            SnapshotRequest("vol-123", "ec-123", "mervin.hemaraju", "#CHN-7303"),
            SnapshotRequest("vol-124", "ec-123", "mervin.hemaraju", "#CHN-7303"),
            SnapshotRequest("vol-123", "ec-123", "mervin.hemaraju", "#CHN-7303"),
            SnapshotRequest("vol-125", "ec-123", "mervin.hemaraju", "#CHN-7303"),
            SnapshotRequest("vol-125", "ec-123", "mervin.hemaraju", "#CHN-7303"),
        ],
        ["vol-123", "vol-124", "vol-125"]
        ),
        ([
            SnapshotRequest("vol-123", "ec-123", "charles", "#CHN-7303"),
            SnapshotRequest("vol-123", "ec-13", "Ray", "#CHN-7303"),
            SnapshotRequest("vol-123", "ec-3", "mervin", "#CHN-7303"),
        ],
        ["vol-123"]
        ),
        ([
            SnapshotRequest("vol-124", "ec-123", "mervin", "#CHN-7303"),
            SnapshotRequest("vol-125", "ec-123", "mervin", "#CHN-7303"),
            SnapshotRequest("vol-126", "ec-123", "mervin", "#CHN-7303"),
        ],
        ["vol-124","vol-125","vol-126"]
        ),
        ([
            SnapshotRequest("vol-124", "ec-123", "mervin", "#CHN-7303"),
            SnapshotRequest("vol-126", "ec-123", "mervin", "#CHN-7303"),
            SnapshotRequest("vol-126", "ec-123", "mervin", "#CHN-7303"),
        ],
        ["vol-124","vol-126"]
        ),
    ]
    @pytest.mark.parametrize("test_data,expected_result", testdata)
    def test_remove_duplicate_snapshots(self,test_data, expected_result):
        
        # Act
        new_list = Helper.remove_duplicate_snapshots(test_data)
        result = []
        
        for request in new_list:
            result.append(request.volume_id)

        # Assert
        assert result == expected_result
        assert len(result) == len(expected_result)

    testdata = [
        ("1.1.1.1", True),
        ("10.10.10.10", True),
        ("1.10.100.255", True),
        ("255.255.255.255", True),
        ("192.168.100.", False),
        ("300.168.100.1", False),
        ("1.168.100.300", False),
        ("192.168..1", False),
        ("192..1.1", False),
        (".1.1.1", False),
        ("hello.168.100.1", False),
        ("t.r.s.a", False),
        ("100.1.1.1:20", False),
    ]
    @pytest.mark.parametrize("test_data,expected_result", testdata)
    def test_is_an_ip_address(self,test_data,expected_result):
        # Arrange

        # Act
        result = Helper.is_an_ip_address(test_data)

        # Assert
        assert result == expected_result