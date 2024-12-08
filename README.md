# Web Scraping Bot

A modular web scraping application that collects product data and displays it through a Dash web interface. The application uses SQLite for data storage and can be deployed using Docker with Nginx as a reverse proxy.

## Features

- Web scraping with BeautifulSoup4
- SQLite database for data storage
- Dash web interface for data visualization
- Docker containerization
- Nginx reverse proxy with SSL support
- Cloudflare IP protection
- Comprehensive test coverage

## Prerequisites

- Python 3.12+
- Docker and Docker Compose (for containerized deployment)
- Nginx (for production deployment)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ykzio-python
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # For Linux/MacOS
venv\Scripts\activate     # For Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Setup

### Development Environment

1. Run the setup script with development configuration:
```bash
chmod +x setup.sh
./setup.sh --dev
```

This will:
- Create necessary Nginx directories
- Generate self-signed SSL certificates
- Set appropriate permissions

### Production Environment

1. Run the setup script with production configuration:
```bash
./setup.sh --prod --update-cf
```

This will:
- Create necessary Nginx directories
- Update Cloudflare IP ranges
- Set up production configuration

## Running the Application

### Local Development

1. Initialize the database:
```bash
python migration_script.py
```

2. Start the application:
```bash
python main.py
```

The application will be available at `http://localhost:8080`

### Docker Deployment

1. Build and start the containers:
```bash
docker-compose up -d
```

The application will be available at:
- HTTP: `http://localhost:80`
- HTTPS: `https://localhost:443`

## Testing

Run the test suite:
```bash
pytest
```

## Project Structure

- `app_runner.py`: Main Dash application logic
- `db_manager.py`: Database management functionality
- `scraper.py`: Web scraping implementation
- `migration_script.py`: Database migration utilities
- `setup.sh`: Environment setup script
- `docker-compose.yml`: Docker composition configuration
- `Dockerfile`: Container build instructions

## Database Schema

The application uses SQLite with the following schema:

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    price REAL NOT NULL,
    delivery_time TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- BeautifulSoup4 for web scraping
- Dash for the web interface
- Docker for containerization
- Nginx for reverse proxy

## Support

If you encounter any issues or have questions, please file an issue in the repository's issue tracker.