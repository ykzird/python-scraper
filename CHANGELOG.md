# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Added
- Initial setup of the project with modular structure.
- Web scraping functionality using BeautifulSoup and requests.
- CSV initialization and management.
- Dash application for displaying scraped data.
- Logging for all critical activities and errors.
- Unit tests for `csv_manager` and `scraper`.

---

## [1.0.0] - 2024-12-06
### Added
- Initial release of the project.

## [1.0.1] - 2024-12-07
### Changed
- Replaced CSV implementation with SQLite3 implementation

## [1.0.2] - 2024-12-07
### Changed
- Added Dockerfile to deploy application with docker
- Added additional logging in refresh_data function