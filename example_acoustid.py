#!/usr/bin/env python3
"""
Example usage of the AcoustID module.

This script demonstrates how to use the AcoustID client to:
1. Lookup audio fingerprints
2. Lookup track IDs
3. Submit fingerprints (requires user API key)
4. Check submission status
5. List AcoustIDs by MusicBrainz ID

Before running:
1. Register your application at https://acoustid.org/new-application to get an API key
2. Replace 'YOUR_API_KEY' below with your actual API key
"""

try:
    from hifiberry_vu.acoustid import AcoustIDClient, AcoustIDError
except ImportError:
    from acoustid import AcoustIDClient, AcoustIDError


def example_lookup_fingerprint():
    """Example: Lookup audio fingerprint and retrieve metadata."""
    print("\n=== Example: Lookup Fingerprint ===")
    
    # Initialize client with your API key
    client = AcoustIDClient(api_key='YOUR_API_KEY')
    
    # Example fingerprint (this is a truncated example - real fingerprints are much longer)
    duration = 641  # seconds
    fingerprint = 'AQABz0qUkZK4oOfhL-CPc4e5C_wW2H2QH9uDL4cvoT8UNQ-eHtsE8cceeFJx...'
    
    try:
        # Lookup with full metadata
        result = client.lookup_fingerprint(
            duration=duration,
            fingerprint=fingerprint,
            meta=['recordings', 'releasegroups', 'compress']
        )
        
        if result['status'] == 'ok':
            print(f"Found {len(result['results'])} matches:")
            for match in result['results']:
                print(f"\n  Track ID: {match['id']}")
                print(f"  Score: {match['score']}")
                
                if 'recordings' in match:
                    for recording in match['recordings']:
                        print(f"  Title: {recording.get('title', 'Unknown')}")
                        if 'artists' in recording:
                            artists = ', '.join([a['name'] for a in recording['artists']])
                            print(f"  Artist(s): {artists}")
                        if 'releasegroups' in recording:
                            for rg in recording['releasegroups']:
                                print(f"  Album: {rg.get('title', 'Unknown')}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except AcoustIDError as e:
        print(f"AcoustID error: {e}")


def example_lookup_track_id():
    """Example: Lookup metadata by AcoustID track ID."""
    print("\n=== Example: Lookup Track ID ===")
    
    client = AcoustIDClient(api_key='YOUR_API_KEY')
    
    # Example track ID
    track_id = '9ff43b6a-4f16-427c-93c2-92307ca505e0'
    
    try:
        result = client.lookup_track_id(
            track_id=track_id,
            meta=['recordings', 'releasegroups']
        )
        
        if result['status'] == 'ok' and result['results']:
            match = result['results'][0]
            print(f"Track ID: {match['id']}")
            
            if 'recordings' in match:
                for recording in match['recordings']:
                    print(f"MusicBrainz Recording ID: {recording['id']}")
                    print(f"Title: {recording.get('title', 'Unknown')}")
                    
    except AcoustIDError as e:
        print(f"AcoustID error: {e}")


def example_submit_fingerprint():
    """Example: Submit audio fingerprint to the database."""
    print("\n=== Example: Submit Fingerprint ===")
    
    client = AcoustIDClient(api_key='YOUR_API_KEY')
    
    # User API key (obtained after signing in at acoustid.org)
    user_api_key = 'USER_API_KEY'
    
    # Prepare submission
    submissions = [{
        'duration': 641,
        'fingerprint': 'AQABz0qUkZK4oOfhL...',
        'mbid': '4e0d8649-1f89-44f3-91af-4c0dbee81f28',  # MusicBrainz recording ID
        'track': 'High Hopes',
        'artist': 'Pink Floyd',
        'album': 'The Division Bell',
        'year': 1994,
        'trackno': 11
    }]
    
    try:
        result = client.submit(
            user_api_key=user_api_key,
            submissions=submissions,
            client_version='1.0'
        )
        
        if result['status'] == 'ok':
            for submission in result['submissions']:
                print(f"Submission ID: {submission['id']}")
                print(f"Status: {submission['status']}")
                if 'result' in submission:
                    print(f"Track ID: {submission['result']['id']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except AcoustIDError as e:
        print(f"AcoustID error: {e}")


def example_batch_submit():
    """Example: Submit multiple fingerprints in one request."""
    print("\n=== Example: Batch Submit ===")
    
    client = AcoustIDClient(api_key='YOUR_API_KEY')
    user_api_key = 'USER_API_KEY'
    
    # Submit multiple tracks at once
    submissions = [
        {
            'duration': 641,
            'fingerprint': 'AQABz0qUkZ...',
            'track': 'Track 1',
            'artist': 'Artist 1'
        },
        {
            'duration': 320,
            'fingerprint': 'AQABxyzabc...',
            'track': 'Track 2',
            'artist': 'Artist 2'
        }
    ]
    
    try:
        result = client.submit(user_api_key=user_api_key, submissions=submissions)
        
        if result['status'] == 'ok':
            print(f"Submitted {len(result['submissions'])} fingerprints")
            for submission in result['submissions']:
                print(f"  Index: {submission.get('index', 'N/A')}")
                print(f"  ID: {submission['id']}, Status: {submission['status']}")
                
    except AcoustIDError as e:
        print(f"AcoustID error: {e}")


def example_check_submission_status():
    """Example: Check status of previously submitted fingerprints."""
    print("\n=== Example: Check Submission Status ===")
    
    client = AcoustIDClient(api_key='YOUR_API_KEY')
    
    # Check status of submissions
    submission_ids = [123456789, 123456790]
    
    try:
        result = client.get_submission_status(submission_ids)
        
        if result['status'] == 'ok':
            for submission in result['submissions']:
                print(f"\nSubmission ID: {submission['id']}")
                print(f"Status: {submission['status']}")
                
                if submission['status'] == 'imported' and 'result' in submission:
                    print(f"Track ID: {submission['result']['id']}")
                elif submission['status'] == 'pending':
                    print("Still processing...")
                    
    except AcoustIDError as e:
        print(f"AcoustID error: {e}")


def example_list_by_mbid():
    """Example: List AcoustIDs by MusicBrainz recording ID."""
    print("\n=== Example: List by MBID ===")
    
    client = AcoustIDClient(api_key='YOUR_API_KEY')
    
    # MusicBrainz recording ID
    mbid = '4e0d8649-1f89-44f3-91af-4c0dbee81f28'
    
    try:
        result = client.list_by_mbid(mbid)
        
        if result['status'] == 'ok':
            print(f"MusicBrainz ID: {mbid}")
            if 'tracks' in result:
                print(f"Found {len(result['tracks'])} AcoustID tracks:")
                for track in result['tracks']:
                    print(f"  - {track['id']}")
                    
    except AcoustIDError as e:
        print(f"AcoustID error: {e}")


def example_rate_limiting():
    """Example: Demonstrate automatic rate limiting."""
    print("\n=== Example: Rate Limiting ===")
    
    # Client with rate limit of 3 requests per second
    client = AcoustIDClient(api_key='YOUR_API_KEY', rate_limit=3)
    
    track_id = '9ff43b6a-4f16-427c-93c2-92307ca505e0'
    
    print("Making 5 rapid requests (rate limited to 3/second)...")
    start_time = __import__('time').time()
    
    try:
        for i in range(5):
            result = client.lookup_track_id(track_id, meta=['recordingids'])
            elapsed = __import__('time').time() - start_time
            print(f"Request {i+1} completed at {elapsed:.2f}s")
            
        total_time = __import__('time').time() - start_time
        print(f"\nTotal time: {total_time:.2f}s (should be ~1.33s with 3/sec limit)")
        
    except AcoustIDError as e:
        print(f"AcoustID error: {e}")


def main():
    """Run all examples."""
    print("AcoustID Python Module Examples")
    print("=" * 50)
    print("\nNOTE: Replace 'YOUR_API_KEY' with your actual API key from")
    print("https://acoustid.org/new-application before running these examples.")
    print("\nUncomment the examples you want to run:")
    
    # Uncomment the examples you want to run:
    
    # example_lookup_fingerprint()
    # example_lookup_track_id()
    # example_submit_fingerprint()
    # example_batch_submit()
    # example_check_submission_status()
    # example_list_by_mbid()
    # example_rate_limiting()


if __name__ == '__main__':
    main()
