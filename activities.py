from uuid import uuid4
from googleapiclient.discovery import build
from requests import request
import json
import random
import numpy as np
import requests
from math import floor
from flashbot_secrets import SLIDES_MASTER_ID, MURAL_CLIENT, MURAL_SECRET, MURAL_ACCESS_TOKEN, MURAL_REFRESH_TOKEN, MURAL_WORKSPACE_ID, MURAL_ROOM_ID

HEX_COLOR_POSTIT_YELLOW = "#FCFE7DFF"
HEX_COLOR_LIGHT_GREEN = "#B5E5CFFF"

async def stoplight(ctx, creds, terms):
    service = build('slides', 'v1', credentials=creds)

    presentation = service.presentations().get(presentationId=SLIDES_MASTER_ID).execute()
    slides = presentation.get('slides')
    number_of_slides = len(slides)

    new_slide_uuid = str(uuid4())
    MAX_TERMS = 6

    # Create a new square textbox, using the supplied element ID.
    requests = [
        {
            'duplicateObject': {
                'objectId': ACTIVITY_INFO['stoplight']['slide_id'],
                'objectIds': {
                    ACTIVITY_INFO['stoplight']['slide_id']: new_slide_uuid
                }
            },
        },
        {
            "replaceAllText": {
                "replaceText": ACTIVITY_INFO['stoplight']['name'],
                "pageObjectIds": [new_slide_uuid],
                "containsText": {
                    "text": "Template slide - " + ACTIVITY_INFO['stoplight']['name'],
                    "matchCase": False
                }
            },
        }
    ]

    for i in range(MAX_TERMS):
        requests.append({
            "replaceAllText": {
                "replaceText": terms[i] if 0 <= i < len(terms) else " ",
                "pageObjectIds": [new_slide_uuid],
                "containsText": {
                    "text": "Topic " + str(i + 1),
                    "matchCase": True
                }
            },
        })

    requests.append({
        "updateSlidesPosition": {
            "slideObjectIds": [new_slide_uuid],
            "insertionIndex": number_of_slides + 1
        }
    })

    # Execute the request.
    body = {
        'requests': requests
    }

    response = service.presentations().batchUpdate(presentationId=SLIDES_MASTER_ID, body=body).execute()
    new_slide_id = response['replies'][0]['duplicateObject']['objectId']

    await ctx.send('A Stop Light slide has been created! Copy it from here into your own presentation: <https://docs.google.com/presentation/d/' + SLIDES_MASTER_ID + '/view#slide=id.' + new_slide_id + ">")

async def catastrophe(ctx, mural_name, terms):
    baseURL = "https://app.mural.co"
    authBaseURL = baseURL + "/api/public/v1/authorization/oauth2"
    tokenURL = baseURL + "/api/public/v1/authorization/oauth2/token"
    scope= "murals:read murals:write"
    
    #mural = OAuth2Session(MURAL_CLIENT, scope=scope)
    #authURL, state = mural.authorization_url(authBaseURL)
    #print("Auth:", authURL)

    #request = requests.post('https://app.mural.co/api/public/v1/authorization/oauth2/token', headers={'Content-Type': 'application/x-www-form-urlencoded'}, data={'client_id': MURAL_CLIENT, 'client_secret': MURAL_SECRET, 'redirect_uri': 'http://localhost:8005', 'code': 'account_code', 'grant_type': 'authorization_code'})
    #print("Code:", request)
    #print(request.json())
    request = requests.post('https://app.mural.co/api/public/v1/authorization/oauth2/token', headers={'Content-Type': 'application/x-www-form-urlencoded'}, data={'client_id': MURAL_CLIENT, 'client_secret': MURAL_SECRET, 'redirect_uri': 'http://localhost:8005', 'refresh_token': MURAL_REFRESH_TOKEN, 'grant_type': 'refresh_token'})
    
    if request.status_code == 200:
        access_token = request.json()['access_token']
        mural_id = mural_create(access_token, MURAL_WORKSPACE_ID, MURAL_ROOM_ID, mural_name)
        
        width = (floor(len(terms) / 10) * 600) + 900
        height = (floor(len(terms) / 10) * 400) + 700

        placeAllStickies(mural_id, access_token, {'x': 50, 'y': 50, 'width': width, 'height': height}, 150, 150, terms)
        mural_add_shape(mural_id, access_token, 'square', 50, 50, width, height)
        await ctx.send("Here's a Catastrophe mural for you! Facilitator link (for SIL, requires login): <" + mural_get_member_link(mural_id, access_token) + ">\nGuest link (for students or SIL): <" + mural_get_visitor_link(mural_id, access_token) + ">")

async def mural(ctx, mural_name):
    request = requests.post('https://app.mural.co/api/public/v1/authorization/oauth2/token', headers={'Content-Type': 'application/x-www-form-urlencoded'}, data={'client_id': MURAL_CLIENT, 'client_secret': MURAL_SECRET, 'redirect_uri': 'http://localhost:8005', 'refresh_token': MURAL_REFRESH_TOKEN, 'grant_type': 'refresh_token'})

    if request.status_code == 200:
        access_token = request.json()['access_token']
        mural_id = mural_create(access_token, MURAL_WORKSPACE_ID, MURAL_ROOM_ID, mural_name)

        await ctx.send("Here's a new mural for you! Facilitator link (for SIL, requires login): <" + mural_get_member_link(mural_id, access_token) + ">\nGuest link (for students or SIL): <" + mural_get_visitor_link(mural_id, access_token) + ">")

async def answer_quest(ctx, mural_name, terms):
    request = requests.post('https://app.mural.co/api/public/v1/authorization/oauth2/token', headers={'Content-Type': 'application/x-www-form-urlencoded'}, data={'client_id': MURAL_CLIENT, 'client_secret': MURAL_SECRET, 'redirect_uri': 'http://localhost:8005', 'refresh_token': MURAL_REFRESH_TOKEN, 'grant_type': 'refresh_token'})

    if request.status_code == 200:
        access_token = request.json()['access_token']
        mural_id = mural_create(access_token, MURAL_WORKSPACE_ID, MURAL_ROOM_ID, mural_name)
        
        width = 9000
        height = 6000

        placeAllStickies(mural_id, access_token, {'x': 50, 'y': 50, 'width': width, 'height': height}, 300, 300, terms['terms'], HEX_COLOR_LIGHT_GREEN, 45)
        placeAllStickies(mural_id, access_token, {'x': 50, 'y': 50, 'width': width, 'height': height}, 500, 300, terms['definitions'], HEX_COLOR_POSTIT_YELLOW, 45)

        await ctx.send("Here's a Answer Quest mural for you! Facilitator link (for SIL, requires login): <" + mural_get_member_link(mural_id, access_token) + ">\nGuest link (for students or SIL): <" + mural_get_visitor_link(mural_id, access_token) + ">")

def mural_create( auth_token, workspace_id, room_id, title ):
    # https://developers.mural.co/public/reference/createmural
    url = "https://app.mural.co/api/public/v1/murals"
    headers = { "Accept": "application/json", "Content-Type": "application/json", "Authorization": "Bearer " + auth_token }
    parms = { "workspaceId": workspace_id, "roomId": int(room_id), "title": title }
    response = request("POST", url, headers = headers, json = parms)
    response_json = json.loads( response.text )
    
    msg = ''
    if 'code' in response_json:
        msg += response_json['code'] + ' '
    if 'message' in response_json:
        msg += response_json['message']
    if msg != '':
        print( msg )
        return None
    if 'value' not in response_json:
        print('No value returned')
        return None
    if 'id' not in response_json['value']:
        print('No id returned')
        return None
    return response_json['value']['id']

def mural_add_sticky( mural_id, auth_token, sticky_data ):
    # https://developers.mural.co/public/reference/createstickynote
    url = "https://app.mural.co/api/public/v1/murals/" + mural_id + "/widgets/sticky-note"
    headers = { "Content-Type" : "application/json", "Accept" : "vnd.mural.preview", "Authorization" : "Bearer " + auth_token }
    data = json.dumps(sticky_data)
    response = request("POST", url, headers=headers, data=data)
    response_json = json.loads(response.text)
    
    msg = ""
    if "code" in response_json:
        msg += response_json["code"] + " "
    if "message" in response_json:
        msg += response_json["message"]
    if msg != "":
        print(msg)

def mural_add_shape(mural_id, auth_token, shape: str, x, y, width=10, height=10):
    url = "https://app.mural.co/api/public/v1/murals/" + mural_id + "/widgets/shape"
    headers = { "Content-Type" : "application/json", "Accept" : "vnd.mural.preview", "Authorization" : "Bearer " + auth_token }

    data = json.dumps({'shape': shape, 'x': x, 'y': y, 'width': width, 'height': height})
    response = request("POST", url, headers=headers, data=data)
    response_json = json.loads(response.text)
    
    msg = ""
    if "code" in response_json:
        msg += response_json["code"] + " "
    if "message" in response_json:
        msg += response_json["message"]
    if msg != "":
        print(msg)

def mural_get_member_link(mural_id, auth_token):
    url = "https://app.mural.co/api/public/v1/murals/" + mural_id
    headers = { "Content-Type" : "application/json", "Accept" : "vnd.mural.preview", "Authorization" : "Bearer " + auth_token }

    response = request("GET", url, headers=headers)
    response_json = json.loads(response.text)
    
    msg = ""
    if "code" in response_json:
        msg += response_json["code"] + " "
    if "message" in response_json:
        msg += response_json["message"]
    if msg != "":
        print(msg)

    return response_json['value']['sharingSettings']['link']

def mural_get_visitor_link(mural_id, auth_token, visitor_perm="write", member_perm="write"):
    url = "https://app.mural.co/api/public/v1/murals/" + mural_id + "/visitor-settings"
    headers = { "Content-Type" : "application/json", "Accept" : "vnd.mural.preview", "Authorization" : "Bearer " + auth_token }

    data = json.dumps({'visitors': visitor_perm, 'workspaceMembers': member_perm})
    response = request("PATCH", url, headers=headers, data=data)
    print("***", response, response.status_code)
    response_json = json.loads(response.text)
    
    msg = ""
    if "code" in response_json:
        msg += response_json["code"] + " "
    if "message" in response_json:
        msg += response_json["message"]
    if msg != "":
        print(msg)

    if 'value' in response_json and 'link' in response_json['value']:
        return response_json['value']['link']
    else:
        return "unknown error when getting visitor link: " + response.status_code

def placeAllStickies( mural_id, auth_token, rectangle, sticky_width, sticky_height, text_arr, note_color=HEX_COLOR_POSTIT_YELLOW, font_size=18):
    attempt = 0

    while attempt < 3:
        coords = makeRandomCoords( rectangle, sticky_width, sticky_height )
        stickies_arr = []
        for txt in text_arr:
            try:
                x, y = coords.pop()
                count = 0
                while ( count <= 3 ) and overlaps( x, y, sticky_width, sticky_height, stickies_arr ):
                    x, y = coords.pop()
                    count += 1
                sticky = { "x"      : x, 
                        "y"      : y, 
                        "width"  : sticky_width, 
                        "height" : sticky_height, 
                        "shape"  : "rectangle", 
                        "style"  : { "backgroundColor" : note_color, 'fontSize': font_size }, 
                        "text"   : txt }
                mural_add_sticky( mural_id, auth_token, sticky )
                stickies_arr.append( sticky )
            except IndexError:
                attempt += 1
        
        if len(text_arr) == len(stickies_arr):
            break

        attempt += 1

def makeRandomCoords(rectangle, sticky_width, sticky_height):
    x_start = round( rectangle["x"] + ( 0.5 * sticky_width ) )
    x_end   = round( rectangle["x"] + rectangle["width"] - ( 1.5 * sticky_width ) )
    y_start = round( rectangle["y"] + ( 0.5 * sticky_height ) )
    y_end   = round( rectangle["y"] + rectangle["height"] - ( 1.5 * sticky_height ) )
    x_list = np.arange( x_start, x_end, round( 0.6 * sticky_width ) ).tolist()
    x_list += x_list
    random.shuffle( x_list )
    random.shuffle( x_list )
    y_list = np.arange( y_start, y_end, round( 0.6 * sticky_width ) ).tolist()
    y_list += y_list
    random.shuffle( y_list )
    random.shuffle( y_list )
    x_length = len( x_list )
    y_length = len( y_list )
    list_length = x_length if ( x_length < y_length ) else y_length
    coords = []
    for i in range( list_length ):
        x = x_list[i] + 10 * random.random()
        y = y_list[i] + 10 * random.random()
        coords.append( [ x, y ] )
    return coords

def stickyInsideOverlapsRectangle(sticky, rectangle):
    #
    left_edge_overlaps = False
    if ( sticky["x"] >= rectangle["x"] ) and \
       ( sticky["x"] <= ( rectangle["x"] + rectangle["width"] ) ):
        left_edge_overlaps = True
    #
    right_edge_overlaps = False
    if ( ( sticky["x"] + sticky["width"] ) >= rectangle["x"] ) and \
       ( ( sticky["x"] + sticky["width"] ) <= ( rectangle["x"] + rectangle["width"] ) ):
        right_edge_overlaps = True
    #
    top_edge_overlaps = False
    if ( sticky["y"] >= rectangle["y"] ) and \
       ( sticky["y"] <= ( rectangle["y"] + rectangle["height"] ) ):
        top_edge_overlaps = True
    #
    bottom_edge_overlaps = False
    if ( ( sticky["y"] + sticky["height"] ) >= rectangle["y"] ) and \
       ( ( sticky["y"] + sticky["height"] ) <= ( rectangle["y"] + rectangle["height"] ) ):
        bottom_edge_overlaps = True
    
    if left_edge_overlaps and right_edge_overlaps and top_edge_overlaps and bottom_edge_overlaps:
        return "inside"
    
    if ( left_edge_overlaps or right_edge_overlaps ) and ( top_edge_overlaps or bottom_edge_overlaps ):
        return "overlaps"
    
    return "outside"

def overlaps(x, y, sticky_width, sticky_height, stickies_arr):
    sticky_in = { "x" : x, "y" : y, "width" : sticky_width, "height" : sticky_height }
    for existing_sticky in stickies_arr:
        position = stickyInsideOverlapsRectangle( sticky_in, existing_sticky )
        if ( "overlaps" == position ) or ( "inside" == position ):
            return True
    return False

ACTIVITY_INFO = {'stoplight': {
                  'name': 'Stop Light',
                  'function': stoplight,
                  'syntax': 'To create a Stop Light slide, use the following syntax: !create stoplight [terms separated by commas (min 1, max 6)]',
                  'slide_id': 'g179cef56cbb_0_0',
                 },
                 'catastrophe': {
                  'name': 'Catastrophe',
                  'function': catastrophe,
                  'syntax': "To create a Catastrophe mural, use the following syntax: !create catastrophe [terms separated by commas (min 2). The first term will be used as the mural's name]"
                 },
                 'mural': {
                  'name': 'Mural',
                  'function': mural,
                  'syntax': "To create a mural, use the following syntax: !create mural [new mural name]"
                 },
                 'answer_quest': {
                  'name': 'Answer Quest',
                  'function': answer_quest,
                  'syntax': "To create an Answer Quest mural, use the following syntax: !create answer_quest [mural name,terms (separated by commas)|definitions (separated by commas)]"
                 },
                }