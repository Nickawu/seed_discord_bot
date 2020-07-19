from __future__ import print_function
import discord
from discord.ext import commands
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv
#https://developers.google.com/sheets/api/quickstart/python?authuser=2

slots = { # we can just hardcode the row corresponding to each level/size eg. 180/4 is mapped to row B forever anyways, why suffer?
    '180/4' : 'B',
    '180/5' : 'C',
    '180/6' : 'D',
    '195/4' : 'E',
    '195/5' : 'F',
    '195/6' : 'G',
    '205/4' : 'H',
    '205/5' : 'I',
    '205/6' : 'J',
    '210/4' : 'K',
    '210/5' : 'L',
    '210/6' : 'M',
    '215/4' : 'N',
    '215/5' : 'O',
    '215/6' : 'P',
}


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

load_dotenv()
SHEET_ID = os.getenv('SPREADSHEET_ID')
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

dynamic_range = sheet.values().get(spreadsheetId=SHEET_ID, range='Z2').execute()
# print(dynamic_range['values'][0][0])
dynamic_range = dynamic_range['values'][0][0]
nameslist = sheet.values().get(spreadsheetId=SHEET_ID, range=dynamic_range).execute().get('values',[])
flatnames = [x[0] for x in nameslist] #flatnames is just an in order list of names in the order they appear in the sheet (index + 1) is the sheet row to write to
# print(flatnames)
# values = nameslist.get('values',[])

# for row in nameslist:
#     print(row)

def nicknamelookup(nickdict, possiblename):
    for mainname in nickdict.keys():
        for nickname in nickdict[mainname]:
            if possiblename.lower() == nickname.lower(): #not case sensitive...
                return mainname
    return None

def add_edl_points(nickdict, msgcontent): # we can parse on space assuming everyone registers a 1 word nickname
    #first order of buisness... parse message (ex. "!edlattend 195/4 owen fred adena erin")
    print(msgcontent)
    brokenmsg = msgcontent.split(' ')
    colname = brokenmsg[1]
    namestoadd = brokenmsg[2:]
    sheetnames = []
    for n in namestoadd:
        tmp = nicknamelookup(nickdict,n)
        if tmp != None:
            sheetnames.append(tmp)
    
    for name in sheetnames:
        if name in flatnames:
            print(name)


    # print(brokenmsg)
    # print(colname)
    # print(namestoadd)
    return True 