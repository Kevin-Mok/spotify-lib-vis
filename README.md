# Spotify Library Visualizer

A full-stack web application that visualizes and analyzes your Spotify music library with interactive D3.js charts. Discover insights about your listening habits through artist distribution, genre breakdowns, and audio feature analysis.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Django](https://img.shields.io/badge/Django-2.2-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-required-blue)
![License](https://img.shields.io/badge/License-GPL-yellow)

## Features

- **Artist Distribution** - Circle packing visualization showing which artists dominate your library
- **Genre Breakdown** - Stacked bar charts displaying genre distribution with nested artist composition
- **Audio Feature Analysis** - Scatter plots for track characteristics (danceability, energy, acousticness, valence)
- **Listening History Tracking** - Persistent record of recently played tracks with CSV import/export
- **OAuth2 Authentication** - Secure Spotify login with automatic token refresh

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3, Django 2.2, Django REST Framework 3.9 |
| **Database** | PostgreSQL with psycopg2 adapter |
| **Frontend** | D3.js, Bootstrap/Darkly theme, SASS/SCSS |
| **API Integration** | Spotify Web API with OAuth2 |
| **Additional** | django-tables2, django-filter, django-compressor |

## Getting Started

### Prerequisites

- Python 3.x
- PostgreSQL
- Spotify Developer Account ([Create one here](https://developer.spotify.com/dashboard))

### Installation

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/Kevin-Mok/spotify-lib-vis
   cd spotify-lib-vis
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export SPOTIFY_CLIENT_ID="your_client_id"
   export SPOTIFY_CLIENT_SECRET="your_client_secret"
   ```

5. **Initialize database and start server:**
   ```bash
   cd src && ./reset_db.sh
   ```

6. **Access the application:**
   Open `http://localhost:8000` in your browser

## Architecture

```
src/
├── login/          # OAuth2 authentication flow
├── api/            # Spotify API integration & data processing
├── graphs/         # D3.js visualization endpoints
└── templates/      # Django templates with embedded D3
```

## Why This Project is Interesting

### Technical Highlights

1. **Real-Time API Integration**
   - Implements OAuth2 authorization code flow with automatic token refresh
   - Handles multiple concurrent Spotify API endpoints with rate limit awareness
   - Intelligent batching (50 tracks/request, 100 features/batch) for efficiency

2. **Interactive D3.js Visualizations**
   - Circle packing algorithm with dynamic space allocation
   - Responsive SVG viewBox scaling for device compatibility
   - Dynamic color palette generation based on data cardinality

3. **Efficient Data Modeling**
   - Normalized database schema with Many-to-Many relationships
   - Prevents data duplication across users while enabling per-user queries
   - Query optimization using Django ORM annotations and aggregations

4. **Queue-Based Batch Processing**
   - Configurable batch limits for tracks, features, and artists
   - Processes queued items efficiently to maximize API throughput

### Skills Demonstrated

- **Full-Stack Development**: Django backend with D3.js frontend
- **API Integration**: OAuth2 flows, rate limiting, batch processing
- **Database Design**: Normalized schema, efficient queries
- **Data Visualization**: Interactive charts with real-time updates
- **DevOps**: Environment configuration, database management

## Resume-ready points by variant

### `general`
- Built a full-stack Spotify analytics platform combining Django backend and D3 visualizations to surface actionable listening insights from personal libraries.
- Delivered OAuth2-secured ingestion, normalized storage, and interactive chart experiences for data-rich user exploration.

### `web-dev`
- Implemented interactive D3 dashboards including circle packing, stacked bars, and scatter plots with responsive SVG behavior.
- Built Django template-driven frontend flows that translate complex music data into intuitive, user-facing visual narratives.

### `aws`
- Architected API ingestion and batch-processing workflows with configurable limits, reflecting cloud-oriented throughput and reliability patterns.
- Structured environment-based configuration and scalable data pipelines suited for hosted analytics applications.

### `python`
- Developed Python and Django services for OAuth2 integration, data modeling, and query-efficient analytics endpoints.
- Implemented batch processing and ORM-optimized querying to handle high-volume track, feature, and artist datasets efficiently.

### `aws-web-dev`
- Combined frontend data-visualization delivery with backend pipeline discipline, bridging product UX and infrastructure-aware operations.
- Balanced chart interactivity with ingestion performance to support reliable deployment in cloud-hosted analytics environments.

### `aws-python`
- Built Python analytics workflows with batch queues and API rate-awareness that map directly to cloud deployment scenarios.
- Prioritized maintainable backend architecture for scalable data refresh cycles and infrastructure-integrated monitoring.

### `web-dev-django`
- Implemented Django and D3 integration patterns that map naturally to full-stack Python web applications with data-heavy interfaces.
- Structured reusable backend-to-frontend contracts for robust visualization rendering and future feature expansion.

### `it-support`
- Improved supportability with clear auth-flow boundaries, documented setup steps, and predictable data-pipeline behavior.
- Designed user-facing analytics views that reduce confusion and simplify troubleshooting of ingestion and visualization issues.

### `it-support-aws`
- Built operationally clear batch and OAuth boundaries that help support teams isolate issues in hosted environments.
- Structured configuration and processing flows for faster incident diagnosis across API, database, and visualization layers.

### `sales`
- Framed complex listening analytics into compelling product value, strengthening demo effectiveness and user conversion discussions.
- Combined technical depth and polished visualization storytelling to support persuasive, data-driven product narratives.

### `call-centre`
- Built clear, interpretable charts and workflow messaging that reduce repetitive user questions in high-volume support scenarios.
- Structured onboarding and data-refresh expectations so support responses remain fast, accurate, and consistent.

## Authors

- [Kevin Mok](https://github.com/Kevin-Mok)
- [Chris Shyi](https://github.com/chrisshyi)

## License

This project is licensed under the GPL License - see the [LICENSE.md](LICENSE.md) file for details.
