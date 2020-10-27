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

dlslots = { # we can just hardcode the col corresponding to each level/size eg. 180/4 is mapped to row B forever anyways, why suffer?
    #we can reference the col by offset int rather than letter, easier list indexing later on...
    #if we need more space later on, we can collapse 180/4,180/5,180/6 to 180 and just map all of them is this dict to the same col value
    'king/5' : 1,
    'king/6' : 2,
    'bolg/5' : 3,
    'bolg/6' : 4,
    'snorri/5' : 5,
    'snorri/6' : 6
}

edlslots = {
    '195/5' : 1,
    '195/6' : 2,
    '200/5' : 3,
    '200/6' : 4,
    '205/5' : 5,
    '205/6' : 6,
    '210/5' : 7,
    '210/6' : 8,
    '215/5' : 9,
    '215/6' : 10
}

raidslots = {
    'hrung' : 1,
    'mordy' : 2,
    'necro' : 3,
    'protbase' : 4,
    'protprime' : 5,
    'gele' : 6,
    'bt' : 7,
    'dino' : 8
}

otherslots = {
    'legacy/5' : 1,
    'legacy/6' : 2,
    'heliant/5' : 3,
    'heliant/6' : 4,
    'factions' : 5
}

conversions = {
    'king/5' : 5,
    'king/6' : 10,
    'bolg/5' : 10,
    'bolg/6' : 15,
    'snorri/5' : 10,
    'snorri/6' : 20,
    '195/5' : 10,
    '195/6' : 20,
    '200/5' : 10,
    '200/6' : 20,
    '205/5' : 15,
    '205/6' : 25,
    '210/5' : 15,
    '210/6' : 25,
    '215/5' : 20,
    '215/6' : 30,
    'hrung' : 75,
    'mordy' : 150,
    'necro' : 225,
    'protbase' : 200,
    'protprime' : 300,
    'gele' : 500,
    'bt' : 750,
    'dino' : 1000,
    'legacy/5' : 25,
    'legacy/6' : 75,
    'heliant/5' : 10,
    'heliant/6' : 50,
    'factions' : 50
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

def getgid(bossname, addrow):
    if bossname in list(dlslots.keys()):
        return ("'dl'!A%d:G%d" % (addrow,addrow), dlslots[bossname])
    if bossname in list(edlslots.keys()):
        return ("'edl'!A%d:K%d"% (addrow,addrow), edlslots[bossname])
    if bossname in list(raidslots.keys()):
        return ("'raids'!A%d:I%d"% (addrow,addrow), raidslots[bossname])
    if bossname in list(otherslots.keys()):
        return ("'others'!A%d:F%d"% (addrow,addrow), otherslots[bossname])
    return None

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
            gidtuple= getgid(colname.lower(),addrow)
            if gidtuple == None:
                return False
            changer = sheet.values().get(spreadsheetId=SHEET_ID, range=gidtuple[0]).execute().get('values',[])
            changer[0][gidtuple[1]] = str(int(changer[0][gidtuple[1]]) + 1)
            body = {'values' : changer}
            logger = sheet.values().update(spreadsheetId=SHEET_ID, range=gidtuple[0], valueInputOption="USER_ENTERED", body=body).execute()
            print('SHEET_UPDATE_PLUS_ABSOLUTE: {0} cells updated'.format(logger.get('updatedCells')))

            rangemacro = "'pointpool'!A%d:B%d" % (addrow,addrow)
            changer = sheet.values().get(spreadsheetId=SHEET_ID, range=rangemacro).execute().get('values',[])
            changer[0][1] = str(int(changer[0][1]) + conversions[colname.lower()])
            body = {'values' : changer}
            logger = sheet.values().update(spreadsheetId=SHEET_ID, range=rangemacro, valueInputOption="USER_ENTERED", body=body).execute()
            print('SHEET_UPDATE_PLUS_POOL: {0} cells updated'.format(logger.get('updatedCells')))
        else:
            print("ERRORLOG: name %s not found in flatnames list... (invalid main name, or main name not added to sheet)" % name)

    return rets

def remove_points(ndict, name, pts):
    mainname = nicknamelookup(ndict, name)
    if mainname == None:
        return False
    addrow = flatnames.index(mainname)
    addrow += 2 #0th element of the list is the second row in the spreadsheet...
    rangemacro = "'pointpool'!A%d:B%d" % (addrow,addrow)
    changer = sheet.values().get(spreadsheetId=SHEET_ID, range=rangemacro).execute().get('values',[])
    if int(changer[0][1]) - pts < 0: #cant have negative points....
        return False
    changer[0][1] = str(int(changer[0][1]) - pts)
    body = {'values' : changer}
    logger = sheet.values().update(spreadsheetId=SHEET_ID, range=rangemacro, valueInputOption="USER_ENTERED", body=body).execute()
    print('SHEET_UPDATE_MINUS: {0} cells updated'.format(logger.get('updatedCells')))
    


def getallpoints(mainname): #returns all raid points and edl total
    if mainname not in flatnames:
        return False
    addrow = flatnames.index(mainname)
    addrow += 2 #0th element of the list is the second row in the spreadsheet...
    rangemacro = "'pointpool'!A%d:B%d" % (addrow,addrow)
    changer = sheet.values().get(spreadsheetId=SHEET_ID, range=rangemacro).execute().get('values',[])
    pts = changer[0][1]
    rstring = mainname + " has " + pts + " points\n"
    return rstring