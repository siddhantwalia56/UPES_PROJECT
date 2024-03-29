import jwt
import requests
import json
from time import time

API_KEY = 'sKaNjR_BQoyOaAgnbe_Cpg'
API_SEC = 'GHvOFVD35qURZJLOvFSJsLpzLQTsBYZFlOLB'


def generateToken():
    token = jwt.encode(
        # Create a payload of the token containing API Key & expiration time
        {'iss': API_KEY, 'exp': time() + 5000},
        # Secret used to generate token signature
        API_SEC,
        # Specify the hashing alg
        algorithm='HS256'
        # Convert token to utf-8
    )
    return token


def getUsers():
    headers = {'authorization': 'Bearer %s' % generateToken(),
               'content-type': 'application/json'}

    r = requests.get('https://api.zoom.us/v2/users/', headers=headers)
    for user in r.json()['users']:
        return user['id']


def createMeeting(userId, meetingdetails):
    headers = {'authorization': 'Bearer %s' % generateToken(),
               'content-type': 'application/json'}
    r = requests.post(
        f'https://api.zoom.us/v2/users/{userId}/meetings', headers=headers, data=json.dumps(meetingdetails))

    meeting_info = r.json()
    print(meeting_info)
    # recording_id = meeting_info['recording']['id']
    # response = requests.get(f'https://api.zoom.us/v2/meetings/{meeting_info["id"]}/recordings/{recording_id}/download', headers=headers)
    # if response.status_code == 200:
    #     # save the recording to a specific location
    #     with open('static/zoomAudio/'+recording_id+".mp4" , 'wb') as f:
    #         f.write(response.content)

    return (r.text)


def meeting(details):
    meetingdetails = {"topic": details['topic'],
                      "type": 2,
                      "start_time": details['start_time'],
                      "duration": details['duration'],
                      "timezone": "Europe/Madrid",
                      "agenda": details['agenda'],

                      "recurrence": {"type": 1,
                                     "repeat_interval": 1
                                     },
                      "settings": {"host_video": details['settings']['host_video'],
                                   "participant_video": details['settings']['participant_video'],
                                   "join_before_host": details['settings']['join_before_host'],
                                   "mute_upon_entry": details['settings']['mute_upon_entry'],
                                   "watermark": "true",
                                   "auto_recording": "local",
                                   'recording_type': 'audio_transcript',
                                   'audio_transcript_lang': 'en-US'
                                   }
                      }
    userId = getUsers()
    meetingInfo = createMeeting(userId, meetingdetails)
    return (meetingInfo)
