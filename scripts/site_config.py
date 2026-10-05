"""Shared build/check URL settings; local previews default to the root path."""
import os
import re
from urllib.parse import urlsplit


def site_config(data):
    site_url = os.environ.get('JOURNAL_SITE_URL', data['url']).rstrip('/')
    parsed = urlsplit(site_url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('JOURNAL_SITE_URL must be an absolute site URL without query/fragment')
    base_path = os.environ.get('JOURNAL_BASE_PATH', '').rstrip('/')
    if base_path and not re.fullmatch(r'(?:/[A-Za-z0-9_-]+)+', base_path):
        raise ValueError('JOURNAL_BASE_PATH must be empty or a path such as /naoki-journal')
    return site_url, base_path
