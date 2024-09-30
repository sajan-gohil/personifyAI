import requests
import os

# Replace these with your values
ACCESS_TOKEN = "IGQWRPRURYMU5pamQxTTktallMdlEwOGdiUXN5ejVwRTNYcDZAwYnBBYVhwSzhjTjVESmNTenZAXREVtbmFfTUNYdy1kNW44ZAzQ1bW55TjBvTEtTUXBLMGx4WUlHVFZAPS3d3QXR6RUZAHbnNZAQUdQS2FJZAi1KNVBJZAFEZD"#os.getenv('YOUR_ACCESS_TOKEN')

# Function to fetch user profile information
def fetch_user_profile(user_id, access_token):
    url = f'https://graph.instagram.com/{user_id}'
    params = {
        'fields': 'id,username,account_type,media_count,followers_count,follows_count,media',
        'access_token': access_token
    }
    response = requests.get(url, params=params)
    print(response)
    return response.json()

# Function to fetch media (photos, videos, captions)
def fetch_user_media(user_id, access_token):
    url = f'https://graph.instagram.com/{user_id}/media'
    params = {
        'fields': 'id,caption,media_type,media_url,thumbnail_url,timestamp',
        'access_token': access_token
    }
    response = requests.get(url, params=params)
    return response.json()

# Main execution
if __name__ == "__main__":
    USER_ID = "srg9k" #os.getenv('USER_ID')  

    # user_profile = fetch_user_profile(USER_ID, ACCESS_TOKEN)
    # user_media = fetch_user_media(USER_ID, ACCESS_TOKEN)

    # print("User Profile:")
    # print(user_profile)

    # print("\nUser Media:")
    # for media in user_media.get('data', []):
    #     print(media)
