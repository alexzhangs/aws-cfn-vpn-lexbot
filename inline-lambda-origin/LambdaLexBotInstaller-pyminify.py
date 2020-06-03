_K=False
_J='1.0'
_I='LambdaArn'
_H='messageVersion'
_G='uri'
_F='maxAttempts'
_E='messages'
_D='PlainText'
_C='groupNumber'
_B='content'
_A='contentType'
import os,time,json,boto3
import cfnresponse
print('Loading function')
intent_name='GetNewIpForVpnInstance'
intent=dict(name=intent_name,description='Assign a new IP for a specific VPN instance.',createVersion=True,slots=[{'name':'VpnInstanceName','description':'The value of tag with key=`Name` on the instance.','slotConstraint':'Required','slotType':'AMAZON.AlphaNumeric','valueElicitationPrompt':{_E:[{_A:_D,_B:'Please specify an instance name.',_C:1},{_A:_D,_B:'Which instance?',_C:1}],_F:3},'priority':1,'sampleUtterances':[],'obfuscationSetting':'NONE'}],sampleUtterances=['Get a new IP','Get a new IP for {VpnInstanceName}','Assign a new IP','Assign a new IP for {VpnInstanceName}','Change the IP','Change the IP for {VpnInstanceName}'],confirmationPrompt={_E:[{_A:_D,_B:'The IP address of this instance will be replaced with a new one, are you sure?',_C:1}],_F:3},rejectionStatement={_E:[{_A:_D,_B:'The IP address of this instance will remain untouched.',_C:1}]},dialogCodeHook={_G:os.getenv(_I),_H:_J},fulfillmentActivity={'type':'CodeHook','codeHook':{_G:os.getenv(_I),_H:_J}},parentIntentSignature='')
bot_name='VpnBot'
bot=dict(name=bot_name,description='A Lex robot to interact with VPN service.',createVersion=True,intents=[{'intentName':intent_name}],clarificationPrompt={_E:[{_A:_D,_B:'What can I do for you?',_C:1},{_A:_D,_B:'How can I help you?',_C:1},{_A:_D,_B:'I can help only if you tell me the magic words.',_C:1}],_F:3},abortStatement={_E:[{_A:_D,_B:'Sorry, I could not understand. Goodbye.',_C:1}]},idleSessionTTLInSeconds=300,voiceId='Salli',processBehavior='BUILD',locale='en-US',childDirected=_K,detectSentiment=_K)
bot_alias_name=bot_name
bot_alias=dict(name=bot_name,botName=bot_name)
lex=boto3.client('lex-models',region_name=os.getenv('Region'))
def lambda_handler(event,context):
    H='version';G='$LATEST';E=context;C=event;B='checksum'
    try:
        print('Received event: '+json.dumps(C));D=C['RequestType'];print('request type: {}'.format(D))
        if D=='Create':
            print('creating the intent')
            try:
                A=lex.get_intent(name=intent_name,version=G)
                if A:intent[B]=A[B]
            except lex.exceptions.NotFoundException:pass
            A=lex.put_intent(**intent);bot['intents'][0]['intentVersion']=A[H];print('creating the bot')
            try:
                A=lex.get_bot(name=bot_name,versionOrAlias=G)
                if A:bot[B]=A[B]
            except lex.exceptions.NotFoundException:pass
            A=lex.put_bot(**bot);bot_alias['botVersion']=A[H];print(A);print('publishing the bot')
            try:
                A=lex.get_bot_alias(name=bot_alias_name,botName=bot_name)
                if A:bot_alias[B]=A[B]
            except lex.exceptions.NotFoundException:pass
            A=lex.put_bot_alias(**bot_alias);print(A)
        elif D=='Delete':
            try:print('unpublishing the bot');lex.delete_bot_alias(name=bot_alias_name,botName=bot_name);time.sleep(10);print('deleting the bot');lex.delete_bot(name=bot_name);time.sleep(10);print('deleting the intent');lex.delete_intent(name=intent_name)
            except lex.exceptions.NotFoundException:pass
        elif D=='Update':0
        cfnresponse.send(C,E,cfnresponse.SUCCESS,{})
    except Exception as F:print(F);cfnresponse.send(C,E,cfnresponse.FAILED,{'error':str(F)})
