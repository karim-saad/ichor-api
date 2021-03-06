'''
Entry file for lambda authorizer
'''
import re
import os


def handler(event, _context):
    '''
    Authorization lambda function taken
    '''
    principal_id = os.getenv('PRINCIPAL_ID')

    split_method_arn = event['methodArn'].split(':')
    split_gateway_arn = split_method_arn[5].split('/')
    aws_account_id = split_method_arn[4]

    auth_policy = AuthPolicy(principal_id, aws_account_id)
    auth_policy.rest_api_id = split_gateway_arn[0]
    auth_policy.region = split_method_arn[3]
    auth_policy.stage = split_gateway_arn[1]

    if event['authorizationToken'] == os.getenv('AUTH_TOKEN'):
        auth_policy.allow_all_methods()
    else:
        auth_policy.deny_all_methods()

    auth_response = auth_policy.build()
    return auth_response


class HttpVerb:
    '''
    Verb class for HTTP methods
    '''
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'
    ALL = '*'


class AuthPolicy:
    '''
    Policy class taken from
    https://github.com/awslabs/aws-apigateway-lambda-authorizer-blueprints/blob/master/blueprints/python/api-gateway-authorizer-python.py
    '''
    aws_account_id = ''
    principal_id = ''
    version = '2012-10-17'
    pathRegex = r'^[/.a-zA-Z0-9-\*]+$'
    allow_methods = []
    deny_methods = []

    rest_api_id = '86cucmvei5'
    region = 'ap-southeast-2'
    stage = 'prod'

    def __init__(self, principal, awsAccountId):
        self.aws_account_id = awsAccountId
        self.principal_id = principal
        self.allow_methods = []
        self.deny_methods = []

    def _add_method(self, effect, verb, resource, conditions):
        '''Adds a method to the internal lists of allowed or denied methods. Each object in
        the internal list contains a resource ARN and a condition statement. The condition
        statement can be null.'''
        if verb != '*' and not hasattr(HttpVerb, verb):
            raise NameError('Invalid HTTP verb ' + verb +
                            '. Allowed verbs in HttpVerb class')
        resource_pattern = re.compile(self.pathRegex)
        if not resource_pattern.match(resource):
            raise NameError('Invalid resource path: ' + resource +
                            '. Path should match ' + self.pathRegex)

        if resource[:1] == '/':
            resource = resource[1:]

        resource_arn = ('arn:aws:execute-api:' +
                        self.region + ':' +
                        self.aws_account_id + ':' +
                        self.rest_api_id + '/' +
                        self.stage + '/' +
                        verb + '/' +
                        resource)

        if effect.lower() == 'allow':
            self.allow_methods.append({
                'resourceArn': resource_arn,
                'conditions': conditions
            })
        elif effect.lower() == 'deny':
            self.deny_methods.append({
                'resourceArn': resource_arn,
                'conditions': conditions
            })

    def _get_empty_statement(self, effect):
        '''Returns an empty statement object prepopulated with the correct action and the
        desired effect.'''
        statement = {
            'Action': 'execute-api:Invoke',
            'Effect': effect[:1].upper() + effect[1:].lower(),
            'Resource': []
        }

        return statement

    def _get_statement_for_effect(self, effect, methods):
        '''This function loops over an array of objects containing a resourceArn and
        conditions statement and generates the array of statements for the policy.'''
        statements = []

        if len(methods) > 0:
            statement = self._get_empty_statement(effect)

            for cur_method in methods:
                if cur_method['conditions'] is None or len(cur_method['conditions']) == 0:
                    statement['Resource'].append(cur_method['resourceArn'])
                else:
                    conditional_statement = self._get_empty_statement(effect)
                    conditional_statement['Resource'].append(
                        cur_method['resourceArn'])
                    conditional_statement['Condition'] = cur_method['conditions']
                    statements.append(conditional_statement)

            statements.append(statement)

        return statements

    def allow_all_methods(self):
        '''Adds a '*' allow to the policy to authorize access to all methods of an API'''
        self._add_method('Allow', HttpVerb.ALL, '*', [])

    def deny_all_methods(self):
        '''Adds a '*' allow to the policy to deny access to all methods of an API'''
        self._add_method('Deny', HttpVerb.ALL, '*', [])

    def allow_method(self, verb, resource):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of allowed
        methods for the policy'''
        self._add_method('Allow', verb, resource, [])

    def deny_method(self, verb, resource):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of denied
        methods for the policy'''
        self._add_method('Deny', verb, resource, [])

    def allow_method_with_conditions(self, verb, resource, conditions):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of allowed
        methods and includes a condition for the policy statement. More on AWS policy
        conditions here:
        http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html#Condition'''
        self._add_method('Allow', verb, resource, conditions)

    def deny_method_with_conditions(self, verb, resource, conditions):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of denied
        methods and includes a condition for the policy statement. More on AWS policy
        conditions here:
        http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html#Condition'''
        self._add_method('Deny', verb, resource, conditions)

    def build(self):
        '''Generates the policy document based on the internal lists of allowed and denied
        conditions. This will generate a policy with two main statements for the effect:
        one statement for Allow and one statement for Deny.
        Methods that includes conditions will have their own statement in the policy.'''
        if ((self.allow_methods is None or len(self.allow_methods) == 0) and
                (self.deny_methods is None or len(self.deny_methods) == 0)):
            raise NameError('No statements defined for the policy')

        policy = {
            'principalId': self.principal_id,
            'policyDocument': {
                'Version': self.version,
                'Statement': []
            }
        }

        policy['policyDocument']['Statement'].extend(
            self._get_statement_for_effect('Allow', self.allow_methods))
        policy['policyDocument']['Statement'].extend(
            self._get_statement_for_effect('Deny', self.deny_methods))

        return policy
