"""Tests for the CLI interface."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from etl_client.cli import cli


class TestCLI:
    """Test the CLI interface."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    def test_cli_help(self, runner):
        """Test that CLI help works."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Animal ETL Client' in result.output

    def test_run_command_help(self, runner):
        """Test run command help."""
        result = runner.invoke(cli, ['run', '--help'])
        assert result.exit_code == 0
        assert 'Run the complete ETL pipeline' in result.output

    @patch('etl_client.cli.ETLPipeline')
    def test_run_command_success(self, mock_pipeline_class, runner):
        """Test successful run command execution."""
        # Mock the pipeline
        mock_pipeline = mock_pipeline_class.return_value

        result = runner.invoke(cli, ['run'])

        assert result.exit_code == 0
        assert 'Starting Animal ETL Pipeline' in result.output
        assert 'ETL Pipeline completed successfully' in result.output
        mock_pipeline.run.assert_called_once()

    @patch('etl_client.cli.ETLPipeline')
    def test_run_command_failure(self, mock_pipeline_class, runner):
        """Test run command with pipeline failure."""
        # Mock the pipeline to raise an exception
        mock_pipeline = mock_pipeline_class.return_value
        mock_pipeline.run.side_effect = Exception("Pipeline failed")

        result = runner.invoke(cli, ['run'])

        assert result.exit_code == 1
        assert 'ETL Pipeline failed' in result.output

    @patch('etl_client.cli.ETLPipeline')
    def test_fetch_animal_command(self, mock_pipeline_class, runner):
        """Test fetch-animal command."""
        # Mock the HTTP client
        mock_pipeline = mock_pipeline_class.return_value
        mock_http_client = mock_pipeline.http_client
        mock_http_client.get_animal_details.return_value = {
            "id": 123,
            "name": "Test Animal",
            "born_at": 1640995200000,
            "friends": "Friend1,Friend2"
        }

        result = runner.invoke(cli, ['fetch-animal', '--animal-id', '123'])

        assert result.exit_code == 0
        assert 'Animal 123 details' in result.output
        mock_http_client.get_animal_details.assert_called_once_with(123)

    def test_fetch_animal_missing_id(self, runner):
        """Test fetch-animal command without required animal-id."""
        result = runner.invoke(cli, ['fetch-animal'])

        assert result.exit_code == 2  # Click error for missing parameter
        assert 'Missing option' in result.output

    @patch('etl_client.cli.ETLPipeline')
    def test_list_animals_command(self, mock_pipeline_class, runner):
        """Test list-animals command."""
        # Mock the HTTP client
        mock_pipeline = mock_pipeline_class.return_value
        mock_http_client = mock_pipeline.http_client
        mock_http_client.get_animals_page.return_value = {
            "page": 1,
            "total_pages": 5,
            "items": [
                {"id": 1, "name": "Lion", "born_at": 1640995200000},
                {"id": 2, "name": "Tiger", "born_at": None}
            ]
        }

        result = runner.invoke(cli, ['list-animals', '--page', '1'])

        assert result.exit_code == 0
        assert 'Page 1 of 5' in result.output
        mock_http_client.get_animals_page.assert_called_once_with(1)
