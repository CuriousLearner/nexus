# -*- coding: utf-8 -*-
# Third Party Stuff
import requests
from django.conf import settings
from django.core.cache import cache

# Nexus Stuff
from nexus.base import exceptions as exc


def shorten_url_bitly(long_url):
    """Shorten URL using Bitly API

    :param long_url: The URL to shorten
    :returns: Shortened URL
    """
    if not hasattr(settings, 'BITLY_ACCESS_TOKEN'):
        return long_url  # Return original if no token configured

    # Check cache first
    cache_key = f'bitly_short_{long_url}'
    cached_url = cache.get(cache_key)
    if cached_url:
        return cached_url

    url = 'https://api-ssl.bitly.com/v4/shorten'
    headers = {
        'Authorization': f'Bearer {settings.BITLY_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {'long_url': long_url}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        short_url = response.json()['link']

        # Cache for 30 days
        cache.set(cache_key, short_url, 60 * 60 * 24 * 30)
        return short_url
    except Exception as e:
        # Return original URL if shortening fails
        return long_url


def shorten_url_tinyurl(long_url):
    """Shorten URL using TinyURL API (no auth required)

    :param long_url: The URL to shorten
    :returns: Shortened URL
    """
    # Check cache first
    cache_key = f'tinyurl_short_{long_url}'
    cached_url = cache.get(cache_key)
    if cached_url:
        return cached_url

    url = f'http://tinyurl.com/api-create.php?url={long_url}'

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        short_url = response.text

        # Cache for 30 days
        cache.set(cache_key, short_url, 60 * 60 * 24 * 30)
        return short_url
    except Exception:
        return long_url


def extract_and_shorten_urls(text, service='tinyurl'):
    """Extract URLs from text and replace with shortened versions

    :param text: Text containing URLs
    :param service: URL shortening service ('bitly' or 'tinyurl')
    :returns: Text with shortened URLs
    """
    import re

    if not text:
        return text

    # Regex to find URLs
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    urls = url_pattern.findall(text)

    modified_text = text
    for url in urls:
        if service == 'bitly':
            short_url = shorten_url_bitly(url)
        else:
            short_url = shorten_url_tinyurl(url)

        modified_text = modified_text.replace(url, short_url)

    return modified_text


def track_url_clicks(short_url):
    """Track clicks for a shortened URL (Bitly only)

    :param short_url: The shortened URL to track
    :returns: Dict with click data
    """
    if not hasattr(settings, 'BITLY_ACCESS_TOKEN'):
        return {}

    # Extract link hash from short URL
    link_hash = short_url.split('/')[-1]

    url = f'https://api-ssl.bitly.com/v4/bitlinks/{link_hash}/clicks/summary'
    headers = {
        'Authorization': f'Bearer {settings.BITLY_ACCESS_TOKEN}',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}
