import requests
import pandas as pd
import isodate

API_KEY = "AIzaSyBgx5rfdPc4q2nnGcgdydoh5Y6Jt0qAe9s"
CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"

# Function to get channel summary
def get_channel_summary():
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={CHANNEL_ID}&key={API_KEY}"
    response = requests.get(url).json()

    if "items" in response:
        data = response["items"][0]
        return {
            "Channel Name": data["snippet"]["title"],
            "Total Subscribers": int(data["statistics"]["subscriberCount"]),
            "Total Views": int(data["statistics"]["viewCount"]),
            "Total Videos": int(data["statistics"]["videoCount"]),
            "Country": data["snippet"].get("country", "N/A"),
            "Channel Created": data["snippet"]["publishedAt"]
        }
    return None

# Function to get video summary
def get_video_summary():
    videos = []
    next_page_token = None

    while len(videos) < 100:  # Fetch up to 100 videos
        url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=50"
        if next_page_token:
            url += f"&pageToken={next_page_token}"

        response = requests.get(url).json()

        if "items" not in response:
            break

        video_ids = [item["id"]["videoId"] for item in response["items"] if "videoId" in item["id"]]

        if video_ids:
            details_url = f"https://www.googleapis.com/youtube/v3/videos?key={API_KEY}&id={','.join(video_ids)}&part=snippet,contentDetails,statistics"
            details_response = requests.get(details_url).json()

            if "items" in details_response:
                for item in details_response["items"]:
                    duration = isodate.parse_duration(item["contentDetails"]["duration"]).total_seconds()
                    
                    if duration > 180:  # Exclude Shorts and very short videos
                        videos.append({
                            "Video ID": item["id"],
                            "Title": item["snippet"]["title"],
                            "Publish Date": item["snippet"]["publishedAt"],
                            "Views": int(item["statistics"].get("viewCount", 0)),
                            "Likes": int(item["statistics"].get("likeCount", 0)),
                            "Comments": int(item["statistics"].get("commentCount", 0)),
                            "Duration (sec)": duration
                        })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos[:50]


# Save data to Excel
def save_to_excel():
    channel_data = get_channel_summary()
    video_data = get_video_summary()

    with pd.ExcelWriter("YouTube_Data.xlsx") as writer:
        if channel_data:
            df_channel = pd.DataFrame([channel_data])
            df_channel.to_excel(writer, sheet_name="Channel Summary", index=False)

        if video_data:
            df_videos = pd.DataFrame(video_data)
            df_videos.to_excel(writer, sheet_name="Video Summary", index=False)

# Run the script
save_to_excel()
print("Data saved to YouTube_Data.xlsx")
