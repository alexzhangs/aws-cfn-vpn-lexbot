#!/usr/bin/env python

'''
Create a Lambda Function in a different Region to route the call of Lex Bot
from that Region to current Region.

Environment Variables:
  Region:    Where to create the Lambda Function.
  LambdaArn: Pointing to a desination Lambda Function, it could reside in a
             differnt Region from this Lambda Function.
'''

import os, io, time, zipfile, json, boto3
import cfnresponse # DO NOT change this line, seems CloudFormation reads this to inject the `cfnresponse` package

print('Loading function')

iam_client = boto3.client('iam', region_name=os.getenv('Region'))
lambda_client = boto3.client('lambda', region_name=os.getenv('Region'))

AssumeRolePolicyDocument = {
    'Version': '2012-10-17',
    'Statement': {
        'Effect': 'Allow',
        'Principal': {'Service': ['lambda.amazonaws.com']},
        'Action': ['sts:AssumeRole']
    }
}

InvokeLambdaInlinePolicyDocument = {
    'Version': '2012-10-17',
    'Statement': [{
        'Effect': 'Allow',
        'Action': ['lambda:InvokeFunction'],
        'Resource': '*'
    }]
}

code = [
    'import os, json, boto3',
    '',
    'print(\"Loading function\")',
    '',
    'def lambda_handler(event, context):',
    '    print(\"Received event: \" + json.dumps(event))',
    '',
    '    client = boto3.client(\"lambda\", region_name=os.getenv(\"RoutingLambdaRegion\"))',
    '    response = client.invoke(',
    '        FunctionName=os.getenv(\"RoutingLambdaArn\"),',
    '        Payload=json.dumps(event)',
    '    )',
    '    print(response)',
    '    routed_response = json.loads(response[\"Payload\"].read())',
    '    return routed_response'
]

def prefix(prefix, conjunction, fixed, max_len):
    gap = max_len - len(conjunction) - len(fixed)
    if gap > 0:
        return prefix[0:gap] + conjunction + fixed
    else:
        return fixed

def lambda_handler(event, context):
    try:
        print('Received event: ' + json.dumps(event))
        request_type = event['RequestType']
        print('request type: {}'.format(request_type))

        stack_name = event['StackId'].split('/')[1]
        func_suffix = 'LambdaCrossRegionRouter'
        func_name = prefix(stack_name, '-', func_suffix, 64)
        role_name = prefix(stack_name, '-', func_suffix + 'ExecutionRole', 64)
        lambda_arn = None

        if request_type == 'Create':
            try:
                print('creating the IAM role')
                rr = iam_client.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(AssumeRolePolicyDocument))
                print(rr)

                print('attaching the policy to the IAM role')
                r = iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')
                print(r)

                print('creating the inline policy to the IAM role')
                r = iam_client.put_role_policy(
                    RoleName=role_name,
                    PolicyName='LambdaInvokeLambda',
                    PolicyDocument=json.dumps(InvokeLambdaInlinePolicyDocument))
                print(r)
            except iam_client.exceptions.EntityAlreadyExistsException:
                rr = iam_client.get_role(
                    RoleName=role_name)

            print('generating the zip file in memory for the Lambda function')
            # Zip in file solution
            #zf = zipfile.ZipFile('/tmp/index.zip', mode='w',compression=zipfile.ZIP_DEFLATED)

            # Zip in memory solution
            mem_zip = io.BytesIO()
            zf = zipfile.ZipFile(mem_zip, mode='w',compression=zipfile.ZIP_DEFLATED)

            info = zipfile.ZipInfo('index.py')
            info.external_attr = 0o755 << 16
            zf.writestr(info, '\\n'.join(code))
            zf.close()

            while True:
                try:
                    print('creating the Lambda function')
                    r = lambda_client.create_function(
                        FunctionName=func_name,
                        Runtime='python3.7',
                        Role=rr['Role']['Arn'],
                        Handler='index.lambda_handler',
                        Code={
                            #'ZipFile': open('/tmp/index.zip', 'rb').read()
                            'ZipFile': mem_zip.getvalue()
                        },
                        Description='A Lambda Function to route the cross-region call for the Lex Bot.',
                        Timeout=15,
                        Environment={
                            'Variables': {
                                'RoutingLambdaRegion': os.getenv('RoutingLambdaRegion'),
                                'RoutingLambdaArn': os.getenv('RoutingLambdaArn')
                    }})
                    lambda_arn = r['FunctionArn']
                    print(r)
                    break
                except lambda_client.exceptions.InvalidParameterValueException as e:
                    if e.response['Error']['Message'].find(' role ') > 0:
                        # Error: {'Message': u'The role defined for the function cannot be assumed by Lambda.',
                        #         'Code': 'InvalidParameterValueException'}
                        print('sleep for a while, let the role created in last step take effect.')
                        time.sleep(5)
                    else:
                        raise(e)

            print('adding permission to the Lambda function')
            r = lambda_client.add_permission(
                FunctionName=func_name,
                StatementId=func_suffix + 'InvokePermission-2',
                Action='lambda:InvokeFunction',
                Principal='lex.amazonaws.com',
                SourceArn='arn:aws:lex:{region}:{account}:intent:*'.format(
                    region=os.getenv('Region'),
                    account=os.getenv('RoutingLambdaArn').split(':')[4]
                )
            )
            print(r)
        elif request_type == 'Delete':
            try:
                print('detaching the policy from the IAM role')
                r = iam_client.detach_role_policy(
                    RoleName=role_name,
                    PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')
                print(r)

                print('deleting the inline policy from the IAM role')
                r = iam_client.delete_role_policy(
                    RoleName=role_name,
                    PolicyName='LambdaInvokeLambda')
                print(r)

                print('deleting the IAM role')
                r = iam_client.delete_role(RoleName=role_name)
                print(r)
            except iam_client.exceptions.NoSuchEntityException:
                pass

            try:
                print('deleting the Lambda function')
                r = lambda_client.delete_function(
                    FunctionName=func_name
                )
                print(r)
            except lambda_client.exceptions.ResourceNotFoundException:
                pass
        elif request_type == 'Update':
            pass

        cfnresponse.send(event, context, cfnresponse.SUCCESS, {'LambdaArn': lambda_arn})
    except Exception as e:
        print(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, {'error': str(e)})

