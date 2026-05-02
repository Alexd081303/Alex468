"""
worker.py — Background worker service
Polls the API service every POLL_INTERVAL seconds, fetches game statistics,
and logs a summary to stdout. Demonstrates inter-service REST communication
within the Docker bridge network.
"""

import os
import time
import requests
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [worker] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

API_URL = os.environ.get('API_URL', 'http://api:5000')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', 30))


def check_api_health():
    """Return True if the API service is reachable."""
    try:
        resp = requests.get(f'{API_URL}/health', timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def fetch_game_stats():
    """Fetch genre statistics from the API service."""
    try:
        resp = requests.get(f'{API_URL}/api/games/stats', timeout=5)
        if resp.status_code == 200:
            return resp.json()
        logger.warning('Stats endpoint returned HTTP %s', resp.status_code)
        return None
    except requests.RequestException as e:
        logger.error('Failed to reach API: %s', e)
        return None


def fetch_all_games():
    """Fetch total game count from the API service."""
    try:
        resp = requests.get(f'{API_URL}/api/games', timeout=5)
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.RequestException as e:
        logger.error('Failed to fetch games: %s', e)
        return None


def run():
    logger.info('Worker started. API_URL=%s  POLL_INTERVAL=%ss', API_URL, POLL_INTERVAL)

    # Wait for API service to be ready
    while not check_api_health():
        logger.info('Waiting for API service to be ready...')
        time.sleep(5)

    logger.info('API service is healthy — beginning polling loop.')

    while True:
        logger.info('--- Poll at %s ---', datetime.utcnow().isoformat())

        games_data = fetch_all_games()
        if games_data:
            logger.info('Total games in database: %d', games_data.get('count', 0))

        stats_data = fetch_game_stats()
        if stats_data:
            genre_stats = stats_data.get('genre_stats', [])
            if genre_stats:
                logger.info('Genre breakdown:')
                for entry in genre_stats:
                    logger.info('  %-20s %d game(s)', entry.get('_id', 'Unknown'), entry.get('count', 0))
            else:
                logger.info('No games in the database yet.')

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    run()

