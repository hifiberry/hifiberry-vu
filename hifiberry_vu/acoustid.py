#!/usr/bin/env python3
"""
AcoustID Web Service Client

This module provides a Python interface to the AcoustID Web Service API.
AcoustID is an audio fingerprinting service that can identify music tracks
and retrieve metadata from MusicBrainz.

API Documentation: https://acoustid.org/webservice

Usage Guidelines:
- No commercial usage (free for non-commercial use only)
- Rate limiting: Maximum 3 requests per second
- Requires API key from https://acoustid.org/new-application

Example:
    client = AcoustIDClient(api_key='YOUR_API_KEY')
    result = client.lookup_fingerprint(duration=641, fingerprint='AQABz0qUkZ...')
    if result['status'] == 'ok':
        for match in result['results']:
            print(f"Track ID: {match['id']}, Score: {match['score']}")
"""

import requests
import time
import gzip
from typing import Optional, Dict, List, Any, Union
from io import BytesIO


class AcoustIDError(Exception):
    """Base exception for AcoustID errors."""
    pass


class AcoustIDAPIError(AcoustIDError):
    """Exception raised when API returns an error status."""
    pass


class AcoustIDRateLimitError(AcoustIDError):
    """Exception raised when rate limit is exceeded."""
    pass


class AcoustIDClient:
    """
    Client for interacting with the AcoustID Web Service API.
    
    Attributes:
        api_key: Application API key from https://acoustid.org/new-application
        base_url: Base URL for the API (default: https://api.acoustid.org/v2)
        rate_limit: Maximum requests per second (default: 3)
        compress: Whether to use gzip compression for POST requests (default: True)
    """
    
    BASE_URL = "https://api.acoustid.org/v2"
    DEFAULT_RATE_LIMIT = 3  # requests per second
    
    def __init__(
        self, 
        api_key: str,
        base_url: Optional[str] = None,
        rate_limit: float = DEFAULT_RATE_LIMIT,
        compress: bool = True
    ):
        """
        Initialize the AcoustID client.
        
        Args:
            api_key: Application API key from https://acoustid.org/new-application
            base_url: Optional custom base URL (default: https://api.acoustid.org/v2)
            rate_limit: Maximum requests per second (default: 3)
            compress: Whether to use gzip compression for POST requests (default: True)
        """
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.rate_limit = rate_limit
        self.compress = compress
        
        # Rate limiting state
        self._last_request_time = 0.0
        self._min_interval = 1.0 / rate_limit if rate_limit > 0 else 0.0
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting by sleeping if necessary."""
        if self._min_interval > 0:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < self._min_interval:
                time.sleep(self._min_interval - time_since_last)
            self._last_request_time = time.time()
    
    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        method: str = 'POST'
    ) -> Dict[str, Any]:
        """
        Make a request to the AcoustID API.
        
        Args:
            endpoint: API endpoint (e.g., 'lookup', 'submit')
            params: Request parameters
            method: HTTP method ('GET' or 'POST')
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            AcoustIDAPIError: If API returns error status
            AcoustIDRateLimitError: If rate limit is exceeded
            AcoustIDError: For other errors
        """
        self._enforce_rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        # Add client API key
        params['client'] = self.api_key
        
        # Default to JSON format if not specified
        if 'format' not in params:
            params['format'] = 'json'
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, timeout=30)
            else:  # POST
                if self.compress:
                    # Compress the request body with gzip
                    body = requests.compat.urlencode(params).encode('utf-8')
                    compressed = gzip.compress(body)
                    
                    headers = {
                        'Content-Encoding': 'gzip',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                    response = requests.post(url, data=compressed, headers=headers, timeout=30)
                else:
                    response = requests.post(url, data=params, timeout=30)
            
            response.raise_for_status()
            
            # Parse JSON response
            result = response.json()
            
            # Check for API errors
            if result.get('status') == 'error':
                error_msg = result.get('error', {})
                error_code = error_msg.get('code', 'unknown')
                error_message = error_msg.get('message', 'Unknown error')
                
                if error_code == 'rate_limit_exceeded':
                    raise AcoustIDRateLimitError(f"Rate limit exceeded: {error_message}")
                else:
                    raise AcoustIDAPIError(f"API error ({error_code}): {error_message}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise AcoustIDError(f"Request failed: {e}")
    
    def lookup_fingerprint(
        self,
        duration: int,
        fingerprint: str,
        meta: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Lookup audio fingerprint and retrieve metadata.
        
        Args:
            duration: Duration of the audio file in seconds
            fingerprint: Audio fingerprint data (from Chromaprint)
            meta: List of metadata to include. Options:
                  - 'recordings': MusicBrainz recording metadata
                  - 'recordingids': MusicBrainz recording IDs only
                  - 'releases': Release information
                  - 'releaseids': Release IDs only
                  - 'releasegroups': Release group information
                  - 'releasegroupids': Release group IDs only
                  - 'tracks': Track information
                  - 'compress': Compress metadata
                  - 'usermeta': User-submitted metadata
                  - 'sources': Data sources
                  
        Returns:
            Dictionary containing:
            - status: 'ok' or 'error'
            - results: List of matches with IDs, scores, and requested metadata
            
        Example:
            result = client.lookup_fingerprint(
                duration=641,
                fingerprint='AQABz0qUkZ...',
                meta=['recordings', 'releasegroups', 'compress']
            )
        """
        params = {
            'duration': duration,
            'fingerprint': fingerprint
        }
        
        if meta:
            params['meta'] = '+'.join(meta)
        
        return self._make_request('lookup', params)
    
    def lookup_track_id(
        self,
        track_id: str,
        meta: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Lookup metadata by AcoustID track ID.
        
        Args:
            track_id: AcoustID track ID (UUID)
            meta: List of metadata to include (same options as lookup_fingerprint)
            
        Returns:
            Dictionary containing track metadata
            
        Example:
            result = client.lookup_track_id(
                track_id='9ff43b6a-4f16-427c-93c2-92307ca505e0',
                meta=['recordingids']
            )
        """
        params = {'trackid': track_id}
        
        if meta:
            params['meta'] = '+'.join(meta)
        
        return self._make_request('lookup', params)
    
    def submit(
        self,
        user_api_key: str,
        submissions: List[Dict[str, Any]],
        client_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit audio fingerprints and metadata to the AcoustID database.
        
        Args:
            user_api_key: User's API key (obtained after signing in at acoustid.org)
            submissions: List of submission dictionaries, each containing:
                - duration (required): Duration in seconds
                - fingerprint (required): Audio fingerprint data
                - bitrate (optional): Bitrate of audio file
                - fileformat (optional): File format (MP3, M4A, etc.)
                - mbid (optional): MusicBrainz recording ID
                - track (optional): Track title
                - artist (optional): Track artist
                - album (optional): Album title
                - albumartist (optional): Album artist
                - year (optional): Album release year
                - trackno (optional): Track number
                - discno (optional): Disc number
            client_version: Optional application version string
            
        Returns:
            Dictionary containing:
            - status: 'ok' or 'error'
            - submissions: List of submission results with IDs and status
            
        Example:
            result = client.submit(
                user_api_key='user_key_here',
                submissions=[{
                    'duration': 641,
                    'fingerprint': 'AQABz0qUkZ...',
                    'mbid': '4e0d8649-1f89-44f3-91af-4c0dbee81f28',
                    'track': 'High Hopes',
                    'artist': 'Pink Floyd',
                    'album': 'The Division Bell'
                }]
            )
        """
        params = {'user': user_api_key}
        
        if client_version:
            params['clientversion'] = client_version
        
        # Handle single or batch submissions
        if len(submissions) == 1:
            # Single submission - no index suffix
            params.update(submissions[0])
        else:
            # Batch submission - add index suffix to each parameter
            for idx, submission in enumerate(submissions):
                for key, value in submission.items():
                    params[f'{key}.{idx}'] = value
        
        return self._make_request('submit', params)
    
    def get_submission_status(
        self,
        submission_ids: Union[int, List[int]],
        client_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check the status of previously submitted fingerprints.
        
        Args:
            submission_ids: Single submission ID or list of submission IDs
            client_version: Optional application version string
            
        Returns:
            Dictionary containing:
            - status: 'ok' or 'error'
            - submissions: List of submission statuses
            
        Example:
            result = client.get_submission_status([123456789, 123456790])
        """
        if isinstance(submission_ids, int):
            submission_ids = [submission_ids]
        
        params = {'id': submission_ids}
        
        if client_version:
            params['clientversion'] = client_version
        
        return self._make_request('submission_status', params)
    
    def list_by_mbid(
        self,
        mbids: Union[str, List[str]],
        batch: bool = False
    ) -> Dict[str, Any]:
        """
        List AcoustIDs associated with MusicBrainz recording ID(s).
        
        Args:
            mbids: Single MusicBrainz ID or list of MusicBrainz IDs
            batch: Whether to use batch mode for multiple MBIDs
            
        Returns:
            Dictionary containing AcoustID track IDs for the given MBIDs
            
        Example:
            result = client.list_by_mbid('4e0d8649-1f89-44f3-91af-4c0dbee81f28')
        """
        if isinstance(mbids, str):
            mbids = [mbids]
        
        params = {'mbid': mbids}
        
        if batch:
            params['batch'] = 1
        
        return self._make_request('track/list_by_mbid', params)


# Convenience functions for quick usage
def lookup_fingerprint(
    api_key: str,
    duration: int,
    fingerprint: str,
    meta: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to lookup a fingerprint without creating a client instance.
    
    Args:
        api_key: Application API key
        duration: Duration of audio file in seconds
        fingerprint: Audio fingerprint data
        meta: Optional list of metadata to include
        
    Returns:
        Lookup results dictionary
    """
    client = AcoustIDClient(api_key)
    return client.lookup_fingerprint(duration, fingerprint, meta)


def lookup_track_id(
    api_key: str,
    track_id: str,
    meta: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to lookup a track ID without creating a client instance.
    
    Args:
        api_key: Application API key
        track_id: AcoustID track ID (UUID)
        meta: Optional list of metadata to include
        
    Returns:
        Lookup results dictionary
    """
    client = AcoustIDClient(api_key)
    return client.lookup_track_id(track_id, meta)
