import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
import os
from bardapi import Bard
import requests
import streamlit as st



api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "Youtube_api_key"

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=DEVELOPER_KEY)



def extract_video_id(url):
   v_id = url[-11:]
   return v_id
def get_channel_name(url):
    video_id = extract_video_id(url)
    # Make a request to the YouTube Data API to get video details
    video_details_url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={DEVELOPER_KEY}'
    response = requests.get(video_details_url)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        snippet = data['items'][0]['snippet']
        channel_name = snippet['channelTitle']
        return channel_name
    else:
        return "Channel not found"

def get_comments(video_id, page_token=None):
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,

        pageToken=page_token
    )
    response = request.execute()

    comments = []
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        comments.append([
            comment['authorDisplayName'],
            comment['publishedAt'],
            comment['updatedAt'],
            comment['likeCount'],
            comment['textDisplay']
        ])

    if 'nextPageToken' in response:
        next_page_comments = get_comments(video_id, response['nextPageToken'])
        comments.extend(next_page_comments)

    return comments




def thumbnail_url_and_views(video_id):
  """Gets the thumbnail URL for a YouTube video.

  Args:
    video_id: The ID of the YouTube video.

  Returns:
    The URL of the thumbnail for the video.
  """

  url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={DEVELOPER_KEY}"
  response = requests.get(url)
  data = response.json()
  return data["items"][0]["snippet"]["thumbnails"]["maxres"]["url"]


def analyse():
    # Create a text input field
    channel_name = get_channel_name(url=user_input)
    # Get all comments for the video with ID "0DlSRxEq0W4"
    a = extract_video_id(user_input)
    print(a)
    comments = get_comments(a)

    # Save the comments to a DataFrame
    df = pd.DataFrame(comments, columns=['author', 'published_at', 'updated_at', 'like_count', 'text'])
    comments = df["text"]

    prompt = ""
    for i in range(30):
        prompt = prompt + str(i + 1) + ". " + comments[i]

    Question = "Give an overall review as a third person in very small paragraph, considering all the comments so that it would useful for the content creator to have the review on the good and bad things about the video.The comments are " + prompt

    os.environ["_BARD_API_KEY"] = "Bard_API_Key"
    Review = Bard().get_answer(str(Question))['content']

    print(Review)
    st.write("Channel Name :", channel_name)
    st.write("Text Review", Review)

st.title("Comments Analyser")
user_input = st.text_input("Enter Youtube Url:")


if st.button("Analyse"):
    Thumbnail_url= thumbnail_url_and_views(extract_video_id(user_input))
    st.image(Thumbnail_url)
    analyse()







