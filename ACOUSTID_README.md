# AcoustID Python Module

Python client for the [AcoustID Web Service API](https://acoustid.org/webservice).

## Overview

AcoustID is an audio fingerprinting service that can identify music tracks and retrieve metadata from MusicBrainz. This module provides a clean Python interface to the AcoustID REST API.

## Features

- **Fingerprint Lookup**: Identify tracks by audio fingerprint
- **Track ID Lookup**: Get metadata for known AcoustID track IDs
- **Submission**: Submit new fingerprints to the database
- **Batch Operations**: Submit multiple fingerprints in one request
- **Rate Limiting**: Automatic rate limiting (3 requests/second)
- **Compression**: Optional gzip compression for POST requests
- **MusicBrainz Integration**: Retrieve detailed metadata from MusicBrainz

## Installation

The module requires the `requests` library:

```bash
pip install requests
```

## Quick Start

### Get an API Key

1. Register your application at https://acoustid.org/new-application
2. You'll receive an API key for your application

### Basic Usage

```python
from hifiberry_vu.acoustid import AcoustIDClient

# Initialize client
client = AcoustIDClient(api_key='YOUR_API_KEY')

# Lookup a fingerprint
result = client.lookup_fingerprint(
    duration=641,  # seconds
    fingerprint='AQABz0qUkZ...',  # from Chromaprint
    meta=['recordings', 'releasegroups', 'compress']
)

# Process results
if result['status'] == 'ok':
    for match in result['results']:
        print(f"Track ID: {match['id']}")
        print(f"Confidence: {match['score']}")
        
        if 'recordings' in match:
            for recording in match['recordings']:
                print(f"Title: {recording['title']}")
                print(f"Artists: {[a['name'] for a in recording['artists']]}")
```

## API Reference

### AcoustIDClient

Main client class for interacting with the AcoustID API.

#### Constructor

```python
client = AcoustIDClient(
    api_key='YOUR_API_KEY',
    base_url=None,           # Optional custom base URL
    rate_limit=3.0,          # Requests per second
    compress=True            # Use gzip compression
)
```

#### Methods

##### lookup_fingerprint()

Lookup audio fingerprint and retrieve metadata.

```python
result = client.lookup_fingerprint(
    duration=641,                    # Duration in seconds (required)
    fingerprint='AQABz0qUkZ...',    # Chromaprint fingerprint (required)
    meta=['recordings', 'releasegroups']  # Optional metadata
)
```

**Metadata options:**
- `recordings`: Full MusicBrainz recording metadata
- `recordingids`: MusicBrainz recording IDs only
- `releases`: Release information
- `releaseids`: Release IDs only
- `releasegroups`: Release group information
- `releasegroupids`: Release group IDs only
- `tracks`: Track information
- `compress`: Compress metadata
- `usermeta`: User-submitted metadata
- `sources`: Data sources

##### lookup_track_id()

Lookup metadata by AcoustID track ID.

```python
result = client.lookup_track_id(
    track_id='9ff43b6a-4f16-427c-93c2-92307ca505e0',
    meta=['recordingids']
)
```

##### submit()

Submit audio fingerprints and metadata to the database.

```python
result = client.submit(
    user_api_key='USER_API_KEY',  # User's API key (from acoustid.org)
    submissions=[{
        'duration': 641,
        'fingerprint': 'AQABz0qUkZ...',
        'mbid': '4e0d8649-...',      # Optional MusicBrainz ID
        'track': 'Track Title',       # Optional
        'artist': 'Artist Name',      # Optional
        'album': 'Album Title',       # Optional
        'year': 2020,                 # Optional
        'trackno': 1,                 # Optional
        'discno': 1                   # Optional
    }]
)
```

##### get_submission_status()

Check status of previously submitted fingerprints.

```python
result = client.get_submission_status([123456789, 123456790])
```

##### list_by_mbid()

List AcoustIDs associated with MusicBrainz recording ID(s).

```python
result = client.list_by_mbid('4e0d8649-1f89-44f3-91af-4c0dbee81f28')
```

### Convenience Functions

For one-off requests without creating a client instance:

```python
from hifiberry_vu.acoustid import lookup_fingerprint, lookup_track_id

result = lookup_fingerprint(
    api_key='YOUR_API_KEY',
    duration=641,
    fingerprint='AQABz0qUkZ...'
)
```

## Error Handling

The module defines three exception types:

```python
from hifiberry_vu.acoustid import AcoustIDError, AcoustIDAPIError, AcoustIDRateLimitError

try:
    result = client.lookup_fingerprint(duration, fingerprint)
except AcoustIDRateLimitError:
    print("Rate limit exceeded - slow down!")
except AcoustIDAPIError as e:
    print(f"API error: {e}")
except AcoustIDError as e:
    print(f"General error: {e}")
```

## Usage Guidelines

Per AcoustID's [usage guidelines](https://acoustid.org/webservice):

- **Non-commercial use only** (free tier)
- **Rate limit**: Maximum 3 requests per second (enforced automatically)
- **No illegal use**: Don't use with illegal products or services
- **High traffic**: Contact AcoustID if expecting significant traffic

For commercial use, sign up at https://acoustid.biz/

## Examples

See `example_acoustid.py` for complete working examples including:

- Basic fingerprint lookup
- Track ID lookup
- Single and batch submissions
- Submission status checking
- MusicBrainz ID lookup
- Rate limiting demonstration

## Generating Fingerprints

This module handles the API communication. To generate audio fingerprints, use [Chromaprint](https://acoustid.org/chromaprint):

```bash
# Install fpcalc (Chromaprint command-line tool)
sudo apt-get install libchromaprint-tools

# Generate fingerprint
fpcalc -json audio_file.mp3
```

Or use the Python bindings:

```bash
pip install pyacoustid
```

```python
import acoustid

# Generate and lookup in one step
for score, recording_id, title, artist in acoustid.match(api_key, 'audio.mp3'):
    print(f"{title} by {artist} (score: {score})")
```

## Contributing

This is part of the HiFiBerry VU project. For issues or contributions, visit:
https://github.com/hifiberry/hifiberry-vu

## License

See the main project LICENSE file.

## Links

- AcoustID Website: https://acoustid.org/
- API Documentation: https://acoustid.org/webservice
- Chromaprint: https://acoustid.org/chromaprint
- MusicBrainz: https://musicbrainz.org/
