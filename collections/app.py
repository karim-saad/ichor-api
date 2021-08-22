'''
Entry file for collections Lambda
'''
import json

import boto3
from boto3.dynamodb.conditions import Key


def handler(event, _context):
    '''
    Collections lambda function
    '''

    collections_table = boto3.resource('dynamodb').Table('collections')
    split_path = event['path'][1:].split('/')
    path, path_params = split_path[0], split_path[1:]

    if path == 'collections':
        collections = collections_table.scan()['Items']
        return {
            'statusCode': 200,
            'body': json.dumps({
                'collections': collections,
            })
        }

    if path == 'collection':
        collections = collections_table.query(
            IndexName='handle',
            KeyConditionExpression=Key('handle').eq(path_params[0])
        )['Items']
        return {
            'statusCode': 200,
            'body': json.dumps({
                'collection': collections[0]
            })
        }

    return {
        'statusCode': 400,
        'body': 'You messed up.'
    }
