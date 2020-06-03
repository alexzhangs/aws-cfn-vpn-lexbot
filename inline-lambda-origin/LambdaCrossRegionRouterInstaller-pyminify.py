_H='lambda:InvokeFunction'
_G='Allow'
_F='Action'
_E='Effect'
_D='2012-10-17'
_C='Statement'
_B='Version'
_A='Region'
import os,io,time,zipfile,json,boto3
import cfnresponse
print('Loading function')
iam_client=boto3.client('iam',region_name=os.getenv(_A))
lambda_client=boto3.client('lambda',region_name=os.getenv(_A))
AssumeRolePolicyDocument={_B:_D,_C:{_E:_G,'Principal':{'Service':['lambda.amazonaws.com']},_F:['sts:AssumeRole']}}
InvokeLambdaInlinePolicyDocument={_B:_D,_C:[{_E:_G,_F:[_H],'Resource':'*'}]}
code=['import os, json, boto3','','print(\"Loading function\")','','def lambda_handler(event, context):','    print(\"Received event: \" + json.dumps(event))','','    client = boto3.client(\"lambda\", region_name=os.getenv(\"RoutingLambdaRegion\"))','    response = client.invoke(','        FunctionName=os.getenv(\"RoutingLambdaArn\"),','        Payload=json.dumps(event)','    )','    print(response)','    routed_response = json.loads(response[\"Payload\"].read())','    return routed_response']
def prefix(prefix,conjunction,fixed,max_len):
    B=conjunction;A=fixed;C=max_len-len(B)-len(A)
    if C>0:return prefix[0:C]+B+A
    else:return A
def lambda_handler(event,context):
    S='RoutingLambdaRegion';R='LambdaInvokeLambda';Q='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole';P='-';N='RoutingLambdaArn';H=context;C=event
    try:
        print('Received event: '+json.dumps(C));D=C['RequestType'];print('request type: {}'.format(D));I=C['StackId'].split('/')[1];E='LambdaCrossRegionRouter';F=prefix(I,P,E,64);B=prefix(I,P,E+'ExecutionRole',64);O=None
        if D=='Create':
            try:print('creating the IAM role');G=iam_client.create_role(RoleName=B,AssumeRolePolicyDocument=json.dumps(AssumeRolePolicyDocument));print(G);print('attaching the policy to the IAM role');A=iam_client.attach_role_policy(RoleName=B,PolicyArn=Q);print(A);print('creating the inline policy to the IAM role');A=iam_client.put_role_policy(RoleName=B,PolicyName=R,PolicyDocument=json.dumps(InvokeLambdaInlinePolicyDocument));print(A);print('wait for a while, let the role be effective');time.sleep(10)
            except iam_client.exceptions.EntityAlreadyExistsException:G=iam_client.get_role(RoleName=B)
            print('generating the zip file in memory for the Lambda function');J=io.BytesIO();K=zipfile.ZipFile(J,mode='w',compression=zipfile.ZIP_DEFLATED);L=zipfile.ZipInfo('index.py');L.external_attr=493<<16;K.writestr(L,'\\n'.join(code));K.close();print('creating the Lambda function');A=lambda_client.create_function(FunctionName=F,Runtime='python3.7',Role=G['Role']['Arn'],Handler='index.lambda_handler',Code={'ZipFile':J.getvalue()},Description='A Lambda Function to route the cross-region call for the Lex Bot.',Timeout=15,Environment={'Variables':{S:os.getenv(S),N:os.getenv(N)}});O=A['FunctionArn'];print(A);print('adding permission to the Lambda function');A=lambda_client.add_permission(FunctionName=F,StatementId=E+'InvokePermission-2',Action=_H,Principal='lex.amazonaws.com',SourceArn='arn:aws:lex:{region}:{account}:intent:*'.format(region=os.getenv(_A),account=os.getenv(N).split(':')[4]));print(A)
        elif D=='Delete':
            try:print('detaching the policy from the IAM role');A=iam_client.detach_role_policy(RoleName=B,PolicyArn=Q);print(A);print('deleting the inline policy from the IAM role');A=iam_client.delete_role_policy(RoleName=B,PolicyName=R);print(A);print('deleting the IAM role');A=iam_client.delete_role(RoleName=B);print(A)
            except iam_client.exceptions.NoSuchEntityException:pass
            try:print('deleting the Lambda function');A=lambda_client.delete_function(FunctionName=F);print(A)
            except lambda_client.exceptions.ResourceNotFoundException:pass
        elif D=='Update':0
        cfnresponse.send(C,H,cfnresponse.SUCCESS,{'LambdaArn':O})
    except Exception as M:print(M);cfnresponse.send(C,H,cfnresponse.FAILED,{'error':str(M)})
