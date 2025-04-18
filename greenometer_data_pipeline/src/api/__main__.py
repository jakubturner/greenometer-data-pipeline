import argparse
from logging import getLogger

import uvicorn

from ..common.config import API_HOST, API_PORT, ensure_directories

LOGGER = getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Data Processing API")
    parser.add_argument(
        "--host",
        type=str,
        default=API_HOST,
        help=f"Host to bind the API server (default: {API_HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=API_PORT,
        help=f"Port to bind the API server (default: {API_PORT})",
    )
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    return parser.parse_args()


def main() -> None:
    """Main entry point for the API application"""
    # Ensure required directories exist
    ensure_directories()

    # Parse command line arguments
    args = parse_arguments()

    LOGGER.info(f"Starting Data Processing API on http://{args.host}:{args.port}")
    LOGGER.info("Press CTRL+C to stop the server")

    uvicorn.run(
        "greenometer_data_pipeline.src.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
