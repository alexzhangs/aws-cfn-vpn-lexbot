_M=False
_L='1.0'
_K='LambdaArn'
_J='messageVersion'
_I='uri'
_H='The value of tag with key=`Name` on the instance.'
_G='maxAttempts'
_F=True
_E='messages'
_D='PlainText'
_C='groupNumber'
_B='content'
_A='contentType'
import os,json,boto3
import cfnresponse
print('Loading function')
slot_type_name='VpnInstanceNames'
slot_type=dict(name=slot_type_name,description=_H,createVersion=_F,enumerationValues=[dict(value=A)for A in['foo','bar']],valueSelectionStrategy='ORIGINAL_VALUE')
intent_name='GetNewIpForVpnInstance'
intent=dict(name=intent_name,description='Assign a new IP for a specific VPN instance.',createVersion=_F,slots=[{'name':'VpnInstanceName','description':_H,'slotConstraint':'Required','slotType':slot_type_name,'valueElicitationPrompt':{_E:[{_A:_D,_B:'Please specify an instance name.',_C:1},{_A:_D,_B:'Which instance?',_C:1}],_G:3},'priority':1,'sampleUtterances':[],'obfuscationSetting':'NONE'}],sampleUtterances=['Get a new IP for instance {VpnInstanceName}','Assign a new IP for instance {VpnInstanceName}','Change the IP of instance {VpnInstanceName}'],confirmationPrompt={_E:[{_A:_D,_B:'The IP address of this instance will be replaced with a new one, are you sure?',_C:1}],_G:3},rejectionStatement={_E:[{_A:_D,_B:'The IP address of this instance will remain untouched.',_C:1}]},dialogCodeHook={_I:os.getenv(_K),_J:_L},fulfillmentActivity={'type':'CodeHook','codeHook':{_I:os.getenv(_K),_J:_L}},parentIntentSignature='')
bot_name='VpnBot'
bot=dict(name=bot_name,description='A Lex robot to interact with VPN service.',createVersion=_F,intents=[{'intentName':intent_name}],clarificationPrompt={_E:[{_A:_D,_B:'What can I do for you?',_C:1},{_A:_D,_B:'How can I help you?',_C:1},{_A:_D,_B:'I can help only if you tell me the magic words.',_C:1}],_G:3},abortStatement={_E:[{_A:_D,_B:'Sorry, I could not understand. Goodbye.',_C:1}]},idleSessionTTLInSeconds=300,voiceId='Salli',processBehavior='BUILD',locale='en-US',childDirected=_M,detectSentiment=_M)
lex=boto3.client('lex-models',region_name=os.getenv('Region'))
def lambda_handler(event,context):
    H='version';G='$LATEST';E=context;C=event;B='checksum'
    try:
        print('Received event: '+json.dumps(C));D=C['RequestType'];print('request type: {}'.format(D))
        if D=='Create':
            try:
                A=lex.get_slot_type(name=slot_type_name,version=G)
                if A:slot_type[B]=A[B]
            except lex.exceptions.NotFoundException:pass
            A=lex.put_slot_type(**slot_type);intent['slots'][0]['slotTypeVersion']=A[H]
            try:
                A=lex.get_intent(name=intent_name,version=G)
                if A:intent[B]=A[B]
            except lex.exceptions.NotFoundException:pass
            A=lex.put_intent(**intent);bot['intents'][0]['intentVersion']=A[H]
            try:
                A=lex.get_bot(name=bot_name,versionOrAlias=G)
                if A:bot[B]=A[B]
            except lex.exceptions.NotFoundException:pass
            A=lex.put_bot(**bot);print(A)
        elif D=='Delete':
            try:lex.delete_bot(name=bot_name);lex.delete_intent(name=intent_name);lex.delete_slot_type(name=slot_type_name)
            except lex.exceptions.NotFoundException:pass
        elif D=='Update':0
        cfnresponse.send(C,E,cfnresponse.SUCCESS,{})
    except Exception as F:print(F);cfnresponse.send(C,E,cfnresponse.FAILED,{'error':str(F)})
