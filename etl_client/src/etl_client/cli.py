"""Command-line interface for the Animal ETL client."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
import structlog

from .config import settings
from .pipeline import ETLPipeline


def setup_logging() -> None:
    """Configure structured logging."""
    if settings.log_format == "json":
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    else:
        # Plain text logging with colors
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    # Set up standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


@click.group()
@click.option(
    "--config",
    "config_file",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, config_file: Optional[str], verbose: bool) -> None:
    """Animal ETL Client - Process animal data from the Animals API."""
    if config_file:
        # Load custom config file
        import dotenv

        dotenv.load_dotenv(config_file)

    if verbose:
        settings.log_level = "DEBUG"

    setup_logging()
    ctx.ensure_object(dict)


@cli.command()
@click.pass_context
def run(ctx: click.Context) -> None:
    """Run the complete ETL pipeline to process all animals."""
    click.echo("🐾 Starting Animal ETL Pipeline...")
    click.echo(f"API Base URL: {settings.api_base_url}")
    click.echo(f"Batch Size: {settings.batch_size}")
    click.echo(f"Max Workers: {settings.max_workers}")
    click.echo("-" * 50)

    try:
        pipeline = ETLPipeline()
        pipeline.run()
        click.echo("✅ ETL Pipeline completed successfully!")
    except KeyboardInterrupt:
        click.echo("\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ ETL Pipeline failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--animal-id", type=int, required=True, help="Animal ID to fetch")
@click.pass_context
def fetch_animal(ctx: click.Context, animal_id: int) -> None:
    """Fetch details for a specific animal."""
    setup_logging()
    http_client = ETLPipeline().http_client

    try:
        animal_data = http_client.get_animal_details(animal_id)
        click.echo(f"Animal {animal_id} details:")
        click.echo(animal_data)
    except Exception as e:
        click.echo(f"❌ Failed to fetch animal {animal_id}: {e}")
        sys.exit(1)


@cli.command()
@click.option("--page", type=int, default=1, help="Page number to fetch")
@click.pass_context
def list_animals(ctx: click.Context, page: int) -> None:
    """List animals from a specific page."""
    setup_logging()
    http_client = ETLPipeline().http_client

    try:
        page_data = http_client.get_animals_page(page)
        click.echo(f"Page {page} of {page_data['total_pages']}:")
        for animal in page_data["items"]:
            click.echo(
                f"  ID: {animal['id']}, Name: {animal['name']}, Born: {animal.get('born_at', 'Unknown')}"
            )
    except Exception as e:
        click.echo(f"❌ Failed to fetch page {page}: {e}")
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
