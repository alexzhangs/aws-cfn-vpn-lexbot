#!/usr/bin/env python

'''
Create a chat-ready AWS Lex Bot in a specified Region.

Environment Variables:
  Region:    Where to create the Lex Bot.
  LambdaArn: Pointing to a Lambda Function, it must reside in the same Region
             from the Lex Bot.
'''

import os, time, json, boto3
import cfnresponse # DO NOT change this line, seems CloudFormation reads this to inject the `cfnresponse` package

print('Loading function')

intent_name = 'GetNewIpForVpnInstance'
intent = dict(
    name=intent_name,
    description='Assign a new IP for a specific VPN instance.',
    createVersion=True,
    slots=[
        {
            'name': 'VpnInstanceName',
            'description': 'The value of tag with key=`Name` on the instance.',
            'slotConstraint': 'Required',
            'slotType': 'AMAZON.AlphaNumeric',
            'valueElicitationPrompt': {
                'messages': [
                    {
                        'contentType': 'PlainText',
                        'content': 'Please specify an instance name.',
                        'groupNumber': 1
                    },
                    {
                        'contentType': 'PlainText',
                        'content': 'Which instance?',
                        'groupNumber': 1
                    },
                ],
                'maxAttempts': 3,
            },
            'priority': 1,
            'sampleUtterances': [],
            'obfuscationSetting': 'NONE'
        },
    ],
    sampleUtterances=[
        'Get a new IP',
        'Get a new IP for {VpnInstanceName}',
        'Assign a new IP',
        'Assign a new IP for {VpnInstanceName}',
        'Change the IP',
        'Change the IP for {VpnInstanceName}',
    ],
    confirmationPrompt={
        'messages': [
            {
                'contentType': 'PlainText',
                'content': 'The IP address of this instance will be replaced with a new one, are you sure?',
                'groupNumber': 1
            },
        ],
        'maxAttempts': 3,
    },
    rejectionStatement={
        'messages': [
            {
                'contentType': 'PlainText',
                'content': 'The IP address of this instance will remain untouched.',
                'groupNumber': 1
            },
        ],
    },
    dialogCodeHook={
        'uri': os.getenv('LambdaArn'),
        'messageVersion': '1.0'
    },
    fulfillmentActivity={
        'type': 'CodeHook',
        'codeHook': {
            'uri': os.getenv('LambdaArn'),
            'messageVersion': '1.0'
        }
    },
    parentIntentSignature='',
)

bot_name = 'VpnBot'
bot = dict(
    name=bot_name,
    description='A Lex robot to interact with VPN service.',
    createVersion=True,
    intents=[
        {
            'intentName': intent_name
        }
    ],
    clarificationPrompt={
        'messages': [
            {
                'contentType': 'PlainText',
                'content': 'What can I do for you?',
                'groupNumber': 1
            },
            {
                'contentType': 'PlainText',
                'content': 'How can I help you?',
                'groupNumber': 1
            },
            {
                'contentType': 'PlainText',
                'content': 'I can help only if you tell me the magic words.',
                'groupNumber': 1
            },
        ],
        'maxAttempts': 3
    },
    abortStatement={
        'messages': [
            {
                'contentType': 'PlainText',
                'content': 'Sorry, I could not understand. Goodbye.',
                'groupNumber': 1
            },
        ]
    },
    idleSessionTTLInSeconds=300,
    voiceId='Salli',
    processBehavior='BUILD',
    locale='en-US',
    childDirected=False,
    detectSentiment=False,
)

lex = boto3.client('lex-models', region_name=os.getenv('Region'))

def lambda_handler(event, context):
    try:
        print('Received event: ' + json.dumps(event))
        request_type = event['RequestType']
        print('request type: {}'.format(request_type))

        if request_type == 'Create':
            try:
                r = lex.get_intent(
                    name=intent_name,
                    version='$LATEST')
                if r: intent['checksum'] = r['checksum']
            except lex.exceptions.NotFoundException: pass
            r = lex.put_intent(**intent)
            bot['intents'][0]['intentVersion'] = r['version']

            try:
                r = lex.get_bot(
                    name=bot_name,
                    versionOrAlias='$LATEST')
                if r: bot['checksum'] = r['checksum']
            except lex.exceptions.NotFoundException: pass
            r = lex.put_bot(**bot)
            print(r)
        elif request_type == 'Delete':
            try:
                lex.delete_bot(name=bot_name)
                time.sleep(10)
                lex.delete_intent(name=intent_name)
            except lex.exceptions.NotFoundException: pass
        elif request_type == 'Update': pass

        cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
    except Exception as e:
        print(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, {'error': str(e)})

