# aws-cfn-vpn-lexbot

AWS CloudFormation Stack for Lex Chat Bot services.

## Usage

### stack.json

This repo contains a standard AWS CloudFormation template `stack.json`
which can be deployed with AWS web console, AWS CLI or any other AWS
CloudFormation compatible tool.

About how to do this, you may refer to a real-world example
[aws-cfn-vpn](https://github.com/alexzhangs/aws-cfn-vpn).

For the input parameters and the detail of the template, please check the template
file.

## Chat with the Bot

Supported intents:

1. Change node IP address
    * Chat syntax: `Get a new IP[ for <nodename>]`

### 1. by the Amazon Lex Web Console

Visit the [Amazon Lex Web Console](https://console.aws.amazon.com/lex/),
choose the region you created the bot, click the `Test Chatbot` button
in your Bot page. The chatbot should be chat-ready.

### 2. by the 3rd part application, such as Facebook

Check this document out:
[Deploying an Amazon Lex Bot on a Messaging Platform](https://docs.aws.amazon.com/lex/latest/dg/example1.html)

The integration needs to be setup manually.

## For Developers

1. Use inline Lambda functions to avoid the dependency in config files:

    1. Use the `pyminifier` to minimize the size of the Lambda code if
    the code size is greater than 4KB.

    ```
    pip install pyminifier
    pyminify LambdaLexBotInstaller.py > LambdaLexBotInstaller.py
    pyminify LambdaCrossRegionRouterInstaller.py > LambdaCrossRegionRouterInstaller-pyminify.py
    ```

    1. Use `import cfnresponse` as the exact style, to let
    CloudFormation injects `cfnresponse` package for you.

## Troubleshooting

1. The stack creation ends at `CREATE_FAILED` status and Lambda
function LambdaCrossRegionRouterInstaller gives following log:

    ```
    An error occurred (InvalidParameterValueException) when calling
    the CreateFunction operation: The role defined for the function
    cannot be assumed by Lambda.
    ```

    It caused by the unavailable of the role. The role is created but
    is not ready yet. A 10 seconds delay is set for this, but
    sometimes it's not long enough.

    Try to redeploy the stack again, it should go well.
   
1. The stack deletion ends at `DELETE_FAILED` status:  An error
occurred (ConflictException) when calling the DeleteIntent operation:
There is a conflicting operation in progress for the resource named
'GetNewIpForVpnInstance'.
   
    The deletion of the Lex bot is not complete yet. A 10 seconds
    delay is set for this, but sometimes it's not long enough.

    Try to redeploy the stack again, it should go well.
   
1. The Lex bot response in the chat: `foo: the instance name you
   specified does not exist, the valid instance names are: .`

    The instance takes around 15 minutes to register to the
    shadowsocks-manager after the stack creation is complete.

    Try to chat with the Lex bot later.
