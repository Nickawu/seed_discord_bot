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

slots = { # we can just hardcode the col corresponding to each level/size eg. 180/4 is mapped to row B forever anyways, why suffer?
    #we can reference the col by offset int rather than letter, easier list indexing later on...
    #if we need more space later on, we can collapse 180/4,180/5,180/6 to 180 and just map all of them is this dict to the same col value
    '180/4' : 1,
    '180/5' : 2,
    '180/6' : 3,
    '195/4' : 4,
    '195/5' : 5,
    '195/6' : 6,
    '205/4' : 7,
    '205/5' : 8,
    '205/6' : 9,
    '210/4' : 10,
    '210/5' : 11,
    '210/6' : 12,
    '215/4' : 13,
    '215/5' : 14,
    '215/6' : 15,
    'hrung' : 16,
    'mordy' : 17,
    'necro' : 18,
    'gele' : 19,
    'bt' : 20,
    'dino' : 21
}


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

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
dynamic_range = dynamic_range['values'][0][0]
nameslist = sheet.values().get(spreadsheetId=SHEET_ID, range=dynamic_range).execute().get('values',[])
flatnames = [x[0] for x in nameslist] #flatnames is just an in order list of names in the order they appear in the sheet (index + 1) is the sheet row to write to

# range_names = []
# for x in range(2,5):
#     range_names.append("%d:%d" % (x,x))

# print(range_names)
# print(sheet.values().get(spreadsheetId=SHEET_ID, range=range_names).execute().get('valueRanges',[]))


def nicknamelookup(nickdict, possiblename):
    for mainname in nickdict.keys():
        for nickname in nickdict[mainname]:
            if possiblename.lower() == nickname.lower(): #not case sensitive...
                return mainname
    return None

def add_points(nickdict, msgcontent): # we can parse on space assuming everyone registers a 1 word nickname
    #first order of buisness... parse message (ex. "!edlattend 195/4 owen fred adena erin")
    # print(msgcontent)
    brokenmsg = msgcontent.split(' ')
    colname = brokenmsg[1]
    namestoadd = brokenmsg[2:]
    rets = namestoadd.copy()
    sheetnames = []
    for n in namestoadd:
        tmp = nicknamelookup(nickdict,n)
        if tmp != None:
            sheetnames.append(tmp)
            rets.remove(n)
        else:
            print("ERRORLOG: '%s' not found in nickname lookup" % n)
    sheetnames = list(set(sheetnames)) #protect against dups...
    for name in sheetnames:
        if name in flatnames:
            addrow = flatnames.index(name)
            addrow += 2 #0th element of the list is the second row in the spreadsheet...
            if colname.lower() not in slots.keys():
                return False
            rangemacro = "A%d:V%d" % (addrow,addrow) #change v to new col name if we add more categories, or decrease v if we collapse
            changer = sheet.values().get(spreadsheetId=SHEET_ID, range=rangemacro).execute().get('values',[])
            changer[0][slots[colname.lower()]] = str(int(changer[0][slots[colname.lower()]]) + 1)
            body = {'values' : changer}
            logger = sheet.values().update(spreadsheetId=SHEET_ID, range=rangemacro, valueInputOption="USER_ENTERED", body=body).execute()
            print('SHEET_UPDATE_PLUS: {0} cells updated'.format(logger.get('updatedCells')))
        else:
            print("ERRORLOG: name %s not found in flatnames list... (invalid main name, or main name not added to sheet)" % name)

    return rets

def remove_points(mainname, id):
    if mainname not in flatnames:
        return False
    if id not in slots.keys():
        return False
    addrow = flatnames.index(mainname)
    addrow += 2 #0th element of the list is the second row in the spreadsheet...
    rangemacro = "A%d:V%d" % (addrow,addrow) #change v to new col name if we add more categories, or decrease v if we collapse
    changer = sheet.values().get(spreadsheetId=SHEET_ID, range=rangemacro).execute().get('values',[])
    if int(changer[0][slots[id.lower()]]) == 0: #cant have negative points....
        return False
    changer[0][slots[id.lower()]] = str(int(changer[0][slots[id.lower()]]) - 1)
    body = {'values' : changer}
    logger = sheet.values().update(spreadsheetId=SHEET_ID, range=rangemacro, valueInputOption="USER_ENTERED", body=body).execute()
    print('SHEET_UPDATE_MINUS: {0} cells updated'.format(logger.get('updatedCells')))
    


def getallpoints(mainname): #returns all raid points and edl total
    if mainname not in flatnames:
        return False
    retdict = {}
    addrow = flatnames.index(mainname)
    addrow += 2 #0th element of the list is the second row in the spreadsheet...
    rangemacro = "Q%d:V%d" % (addrow,addrow) #change v to new col name if we add more categories, or decrease v if we collapse
    vals = sheet.values().get(spreadsheetId=SHEET_ID, range=rangemacro).execute().get('values',[])[0]
    retdict['hrung --> '] = vals[0]
    retdict['mordy --> '] = vals[1]
    retdict['necro --> '] = vals[2]
    retdict['gele --> '] = vals[3]
    retdict['bt --> '] = vals[4]
    retdict['dino --> '] = vals[5]
    rangemacro = "X%d:X%d" % (addrow,addrow) #change v to new col name if we add more categories, or decrease v if we collapse
    vals = sheet.values().get(spreadsheetId=SHEET_ID, range=rangemacro).execute().get('values',[])[0]
    retdict['EDL_TOTAL --> '] = vals[0]
    
    rstring = ""
    for h in retdict.keys():
        rstring += h
        rstring += retdict[h]
        rstring += '\n'

    return rstring