import pytest
import utils.helper as Helper


class TestHelper:

    testdata = [
        ("snap:server_name0","server_name0"),
        ("snapshot:server_name1","server_name1"),
        ("snapsho:server_name2", None),
        ("server_name2", None),
        ("This is a test", None),
        ("sna:asdas", None),
    ]

    @pytest.mark.parametrize("test_data,expected_result", testdata)
    def test_retrieve_host(self,test_data,expected_result):
        result = Helper.retrieve_host(test_data)
        assert result == expected_result

    testdata = [
        (["ms1", "ms2", "ms3"],'''The results for ticket 1235 are:\nms1\nms2\nms3\n'''),
        (["this is a ms1"],'''The results for ticket 1235 are:\nthis is a ms1\n'''),
        (["ms4", "ms5"],'''The results for ticket 1235 are:\nms4\nms5\n'''),
        ([],'''The results for ticket 1235 are:\n'''),
    ]

    @pytest.mark.parametrize("test_data,expected_result", testdata)
    def test_construct_results_message(self,test_data,expected_result):
        # Arrange
        ticket = "1235"

        # Act
        result = Helper.construct_results_message(test_data, ticket)

        # Assert
        assert result == expected_result

    def test_format_today(self):
        # Arrange
        expected_result = "20210509"

        # Act
        result = Helper.format_today()

        # Assert
        assert expected_result == result
