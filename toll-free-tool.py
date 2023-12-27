# Toll Free Creation tool 

# this tool pulls existing Confing data for Ring to target, and creates a subscriber line (Toll free) and call forwards to Ring To target
# This was created because original Call translation was handled off switch by Toll Free provider
# This syntax is for a very specific switch, this should be addressed if used again


# Notes:
# Currently, CFS name is hardcoded in function create_TFN, this shold be imporved

# import libraries
import sys
import csv
import requests
import getpass
import os
#import random
#import string
from datetime import datetime
from bs4 import BeautifulSoup as bs

# define global variables
username = input("MetaView Web Username:")
password = getpass.getpass()
mvw_ip = input("MetaViewWeb Address: ")
mvw_port = input("MetaViewWeb port: ")
switchversion = input("MetaViewWeb version (example: 9.3): ")
target_list = input("Target List File:")
url="http://{}:{}/mvweb/services/ShService".format(mvw_ip, mvw_port)
headers = {'content-type': 'text/xml'}

# verifys access to MVW before entering a loop and returned error statement
def hello():
    body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sh="http://www.metaswitch.com/srb/soap/sh"> 
    <soapenv:Header/> 
    <soapenv:Body> 
        <sh:ShPull> 
            <sh:UserIdentity></sh:UserIdentity>
            <sh:DataReference>0</sh:DataReference> 
            <sh:ServiceIndication>Meta_Subscriber_BaseInformation</sh:ServiceIndication>
            <sh:OriginHost>?clientVersion={}&amp;ignoreSequenceNumber=true</sh:OriginHost>
        </sh:ShPull> 
    </soapenv:Body>
    </soapenv:Envelope>""".format(switchversion)

    r = requests.post(url,data=body,headers=headers, auth=(username, password))
    response = r.status_code
    
    if response == 200:
        print('Authorized')
        print('Working....')
    else:
        soup = bs(r.content, 'xml')
        f = soup.find('faultstring').text
        print(f)
        exit()

# pull existing LCC Config and save for later
def get_lcc(tn):
    body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sh="http://www.metaswitch.com/srb/soap/sh"> 
                    <soapenv:Header/> 
                    <soapenv:Body> 
                        <sh:ShPull> 
                            <sh:UserIdentity>{}</sh:UserIdentity>
                            <sh:DataReference>0</sh:DataReference> 
                            <sh:ServiceIndication>Meta_Subscriber_LineClassCodes</sh:ServiceIndication>
                            <sh:OriginHost>?clientVersion={}&amp;ignoreSequenceNumber=true</sh:OriginHost>
                        </sh:ShPull> 
                    </soapenv:Body>
                </soapenv:Envelope>""".format(tn,switchversion)
   
    r = requests.post(url,data=body,headers=headers, auth=(username, password))
    soup = bs(r.content, 'xml')

    for result in soup.findAll('ExtendedResult'):
        extcode = result.find('ExtendedResultCode').text
        code = result.find('SubResultCode')
        detail = result.find('SubResultDetail')
        if code is not None:
            code = code.text
        if detail is not None:
            detail = detail.text
        if extcode == '100':
            lcc1=''
            lcc2=''
            lcc3=''
            lcc4=''
            for lcc_1 in soup.findAll('LineClassCode1'):
                lcc1 = lcc1.find('Value').text
            for lcc_2 in soup.findAll('LineClassCode2'):
                lcc2 = lcc2.find('Value').text
            for lcc_3 in soup.findAll('LineClassCode3'):
                lcc3= lcc3.find('Value').text
            for lcc_4 in soup.findAll('LineClassCode4'):
                lcc4 = lcc4.find('Value').text


            output = [lcc1,lcc2,lcc3,lcc4]     
            return output

        else:
            print('>>>>>>>>>ERROR! get_LCC for tn {} CODE:{} DETAIL:{}'.format(tn,code,detail))

# pull existing CustomerInfo Config and save for later
def get_custinfo(tn):
    body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sh="http://www.metaswitch.com/srb/soap/sh"> 
                    <soapenv:Header/> 
                    <soapenv:Body> 
                        <sh:ShPull> 
                            <sh:UserIdentity>{}</sh:UserIdentity>
                            <sh:DataReference>0</sh:DataReference> 
                            <sh:ServiceIndication>Meta_Subscriber_CustomerInformation</sh:ServiceIndication>
                            <sh:OriginHost>?clientVersion={}&amp;ignoreSequenceNumber=true</sh:OriginHost>
                        </sh:ShPull> 
                    </soapenv:Body>
                </soapenv:Envelope>""".format(tn,switchversion)
   
    r = requests.post(url,data=body,headers=headers, auth=(username, password))
    soup = bs(r.content, 'xml')

    for result in soup.findAll('ExtendedResult'):
        extcode = result.find('ExtendedResultCode').text
        code = result.find('SubResultCode')
        detail = result.find('SubResultDetail')
        if code is not None:
            code = code.text
        if detail is not None:
            detail = detail.text
        if extcode == '100':
            lcc1=''
            lcc2=''
            lcc3=''
            lcc4=''
        if extcode == '100':
            custinfo6 =''
            
            for custinfo in soup.findAll('Meta_Subscriber_CustomerInformation'):
                try: 
                    custinfo6 = custinfo.find('CustInfo6').text
                except Exception as e: print('>>>>>>>>ERROR! get_pre_config_base  META RESTORE FILE IS MISSING DATA THIS SUB INVSTIGATE BEFORE RESTORING tn {} type {}'.format(tn,e))

            output = [custinfo6]
            return output

        else:
            print('>>>>>>>>>ERROR! get_custinfo tn {} CODE:{} DETAIL:{}'.format(tn,code,detail))

# create TFTN configuration
def create_TFN(tn,tfn,lcc1,lcc2,lcc3,lcc4,custinfo6):
    body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:user="http://www.metaswitch.com/ems/soap/sh/userdata" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:ser="http://www.metaswitch.com/ems/soap/sh/servicedata">
                <soapenv:Body>
                    <ShUpdate xmlns="http://www.metaswitch.com/srb/soap/sh">
                        <UserIdentity>CFS-1/{}</UserIdentity>
                        <DataReference>0</DataReference>
                        <UserData>
                            <user:Sh-Data xmlns:ns1="http://www.metaswitch.com/srb/soap/sh/userdata">
                            <user:RepositoryData>
                                <user:ServiceIndication>Meta_Subscriber_BaseInformation</user:ServiceIndication>
                                <user:SequenceNumber>0</user:SequenceNumber>
                                <user:ServiceData>
                                    <ser:MetaSwitchData IgnoreSequenceNumber="True" MetaSwitchVersion="9.3.20">
                                        <ser:Meta_Subscriber_BaseInformation>
                                            <ser:NetworkElementName>CFS-1</ser:NetworkElementName>
                                            <ser:MetaSwitchName>CFS-1</ser:MetaSwitchName>
                                            <ser:SubscriberType>IndividualLine</ser:SubscriberType>
                                            <ser:DirectoryNumber>{}</ser:DirectoryNumber>
                                            <ser:SubscriberGroup>All Subscribers New Scheme</ser:SubscriberGroup>
                                            <ser:NumberStatus>Ported to</ser:NumberStatus>
                                            <ser:SignalingType>None</ser:SignalingType>
                                        </ser:Meta_Subscriber_BaseInformation>
                                    </ser:MetaSwitchData>
                                </user:ServiceData>
                            </user:RepositoryData>
                            <user:RepositoryData>
                                <user:ServiceIndication>Meta_Subscriber_LineClassCodes</user:ServiceIndication>
                                <user:SequenceNumber>1</user:SequenceNumber>
                                <user:ServiceData>
                                    <ser:MetaSwitchData IgnoreSequenceNumber="True" MetaSwitchVersion="9.3.20">
                                        <ser:Meta_Subscriber_LineClassCodes>
                                            <ser:LineClassCode1>
                                                <ser:UseDefault>False</ser:UseDefault>
                                                <ser:Value>{}</ser:Value>
                                            </ser:LineClassCode1>
                                            <ser:LineClassCode2>
                                                <ser:UseDefault>False</ser:UseDefault>
                                                <ser:Value>{}</ser:Value>
                                            </ser:LineClassCode2>
                                            <ser:LineClassCode3>
                                                <ser:UseDefault>False</ser:UseDefault>
                                                <ser:Value>{}</ser:Value>
                                            </ser:LineClassCode3>
                                            <ser:LineClassCode4>
                                                <ser:UseDefault>False</ser:UseDefault>
                                                <ser:Value>{}</ser:Value>
                                            </ser:LineClassCode4>
                                        </ser:Meta_Subscriber_LineClassCodes>
                                    </ser:MetaSwitchData>
                                </user:ServiceData>
                            </user:RepositoryData>
                            <user:RepositoryData>
                                <user:ServiceIndication>Meta_Subscriber_CustomerInformation</user:ServiceIndication>
                                <user:SequenceNumber>2</user:SequenceNumber>
                                <user:ServiceData>
                                    <ser:MetaSwitchData xmlns:s="http://www.metaswitch.com/ems/soap/sh/servicedata" MetaSwitchVersion="9.3.20">
                                        <ser:Meta_Subscriber_CustomerInformation>
                                            <ser:CustInfo6>{}_TFN</ser:CustInfo6>
                                        </ser:Meta_Subscriber_CustomerInformation>
                                    </ser:MetaSwitchData>
                                </user:ServiceData>
                            </user:RepositoryData>
                            <user:RepositoryData>
                                <user:ServiceIndication>Meta_Subscriber_UnconditionalCallForwarding</user:ServiceIndication>
                                <user:SequenceNumber>3</user:SequenceNumber>
                                <user:ServiceData>
                                    <ser:MetaSwitchData xmlns:s="http://www.metaswitch.com/ems/soap/sh/servicedata" MetaSwitchVersion="9.3.20">
                                        <ser:Meta_Subscriber_UnconditionalCallForwarding>
                                            <ser:Subscribed Default="True">
                                                <ser:UseDefault>False</ser:UseDefault>
                                                <ser:Value>True</ser:Value>
                                            </ser:Subscribed>
                                            <ser:Variant>
                                                <ser:UseDefault>False</ser:UseDefault>
                                                <ser:Value>Fixed number</ser:Value>
                                            </ser:Variant>
                                            <ser:Enabled>True</ser:Enabled>
                                            <ser:Number>{}</ser:Number>
                                        </ser:Meta_Subscriber_UnconditionalCallForwarding>
                                    </ser:MetaSwitchData>
                                </user:ServiceData>
                            </user:RepositoryData>
                            </user:Sh-Data>
                        </UserData>
                        <OriginHost>?clientVersion={}&amp;ignoreSequenceNumber=True</OriginHost>
                    </ShUpdate>
                </soapenv:Body>
                </soapenv:Envelope>""".format(tfn,tfn,lcc1,lcc2,lcc3,lcc4,custinfo6,tn,switchversion)
    r = requests.post(url,data=body,headers=headers, auth=(username, password))
    soup = bs(r.content, 'xml')

    for result in soup.findAll('ExtendedResult'):
        extcode = result.find('ExtendedResultCode').text
        code = result.find('SubResultCode')
        detail = result.find('SubResultDetail')
        if code is not None:
            code = code.text
        if detail is not None:
            detail = detail.text
        if extcode == '100':
            print('Added TFN {} for sub {} : {}'.format(tfn,tn,custinfo6))

        else:
            print('>>>>>>>>>ERROR! create_TFN {} for sub {} CODE:{} DETAIL:{}'.format(tfn,tn,code,detail))


# def verify_tfn

hello()

#create output files, create headers, direct all print funcitons to log
now = datetime.now()
timestamp = now.strftime("%Y%m%d%H%M%S")
log = open('tftn_log_{}.txt'.format(timestamp),'a')



restore = open('meta_restore_{}.csv'.format(timestamp),'w')
restorehdr = ['tn','sigtype','casigtype','gwname','accdevname','acclinenum','sigfunccode','gr303dial','fskform', 'VisualVM', 'AudibleVM']
restorewriter = csv.writer(restore, delimiter =',')
restorewriter.writerow(restorehdr)
sys.stdout = log

#open list of subs, and start loop
with open(target_list,'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    ontdict={}
    ontportlist=[]
    sipdict={}
    tdmdict={}

    for line in csv_reader:
        
        # assign variables per line
        tn = line[10]
        pswd = get_random_password_string(15)
        ontport = line[7]
        tdmprof = line[2]
        crv = line[3]
        svctag = line[9]
        ont = line[5]
        name = line[11]
        teen = line[12]

        if teen == '0':
            print('*** Begin changes for TN: {} NAME: {}'.format(tn,name))
            baseout = get_pre_config_base(tn)
            vmout = get_pre_config_vm(tn)        
            output = baseout + vmout
            ontdict[ont] = tdmprof
            ontportlist.append(ontport)
            sipdict[ontport]= [tn,pswd] 
            tdmdict[ontport] = [tdmprof,crv,svctag]
            print("Writing current base and VM config to Restore File")
            restorewriter.writerow(output)

            change_SIP(tn, pswd)
            print('*** End changes for TN {}'.format(tn))

        else:
            print('>>>>>>>>>  TN: {} NAME: {} This is a sub line has a Teen Line, will need to migrated manully'.format(tn,name))
    
    
    print("Writing Access Change file")
    change_access(ontportlist,ontdict,sipdict)

    print('Writing Access Restore file')
    restore_access(ontportlist,ontdict,tdmdict)



#close file(s)
restore.close()       
access_change.close()
access_restore.close()
log.close()