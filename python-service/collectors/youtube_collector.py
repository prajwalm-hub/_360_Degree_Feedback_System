import os
from googleapiclient.discovery import build
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YouTubeCollector:
    def __init__(self, config):
        self.config = config
        self.api_key = config.get("youtube_api_key")
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.channels = config.get("youtube_channels", [])

    def get_channel_id(self, channel_name):
        try:
            request = self.youtube.search().list(
                q=channel_name,
                type='channel',
                part='id',
                maxResults=1
            )
            response = request.execute()
            if response['items']:
                return response['items'][0]['id']['channelId']
            return None
        except Exception as e:
            logging.error(f"Error getting channel ID for {channel_name}: {e}")
            return None

    def collect_videos(self):
        collected_videos = []
        for channel_info in self.channels:
            channel_name = channel_info['name']
            channel_id = channel_info.get('id')
            
            if not channel_id:
                logging.info(f"Searching for channel ID for '{channel_name}'...")
                channel_id = self.get_channel_id(channel_name)
                if not channel_id:
                    logging.warning(f"Could not find channel ID for '{channel_name}'. Skipping.")
                    continue
                else:
                    channel_info['id'] = channel_id # Update config with found ID

            logging.info(f"Collecting videos from YouTube channel: {channel_name} (ID: {channel_id})")
            
            try:
                request = self.youtube.search().list(
                    channelId=channel_id,
                    type='video',
                    part='id,snippet',
                    maxResults=self.config.get("youtube_max_results_per_channel", 50),
                    order='date'
                )
                response = request.execute()

                for item in response['items']:
                    video_id = item['id']['videoId']
                    video_details = self._get_video_details(video_id)
                    if video_details:
                        collected_videos.append(self._parse_video_data(video_details, channel_info))
            except Exception as e:
                logging.error(f"Error collecting videos from channel {channel_name} (ID: {channel_id}): {e}")
        return collected_videos

    def _get_video_details(self, video_id):
        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            )
            response = request.execute()
            if response['items']:
                return response['items'][0]
            return None
        except Exception as e:
            logging.error(f"Error fetching details for video {video_id}: {e}")
            return None

    def _parse_video_data(self, video_details, channel_info):
        snippet = video_details['snippet']
        statistics = video_details.get('statistics', {})
        content_details = video_details.get('contentDetails', {})

        upload_date_str = snippet['publishedAt']
        upload_date = datetime.fromisoformat(upload_date_str.replace('Z', '+00:00'))

        # Duration parsing (ISO 8601 format)
        duration_iso = content_details.get('duration', 'PT0S')
        # This would require a more robust parsing for actual duration in seconds/minutes
        # For simplicity, storing as string for now.

        return {
            'id': video_details['id'],
            'title': snippet['title'],
            'description': snippet['description'],
            'channel': snippet['channelTitle'],
            'channel_id': snippet['channelId'],
            'upload_date': upload_date,
            'views': int(statistics.get('viewCount', 0)),
            'likes': int(statistics.get('likeCount', 0)),
            'comments': int(statistics.get('commentCount', 0)),
            'duration': duration_iso,
            'url': f"https://www.youtube.com/watch?v={video_details['id']}",
            'language': channel_info.get('language', 'en'),
            'category': channel_info.get('category', 'Government'),
            'region': channel_info.get('region', 'India'),
            'transcript': None, # To be filled by speech-to-text service
            'sentiment': None,
            'emotions': None,
            'entities': None,
            'summary': None
        }

if __name__ == '__main__':
    # Example Usage (replace with actual config loading and API key)
    # You need to set your YouTube Data API key in your environment variables
    # or directly in the config for testing.
    # For example: export YOUTUBE_API_KEY="YOUR_API_KEY"
    sample_config = {
        "youtube_api_key": os.environ.get("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY"),
        "youtube_channels": [
            {"name": "Narendra Modi", "id": "UCuQy0g1yY-y7_y7_y7_y7_y7", "language": "hi", "category": "Politics", "region": "India"}, # Example ID
            {"name": "DD News", "language": "en", "category": "News", "region": "India"} # Will search for ID
        ],
        "youtube_max_results_per_channel": 10
    }
    
    if sample_config["youtube_api_key"] == "YOUR_YOUTUBE_API_KEY":
        logging.warning("Please set your YOUTUBE_API_KEY environment variable or update the sample_config.")
    else:
        collector = YouTubeCollector(sample_config)
        videos = collector.collect_videos()
        for video in videos:
            print(f"Title: {video['title']}\nChannel: {video['channel']}\nURL: {video['url']}\nUpload Date: {video['upload_date']}\nViews: {video['views']}\n")
