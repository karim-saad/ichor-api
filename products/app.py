'''
Entry file for products Lambda
'''
import json

import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, _context):
    '''
    Products lambda function
    '''

    products_table = boto3.resource('dynamodb').Table('products')
    split_path = event['path'][1:].split('/')
    path, path_params = split_path[0], split_path[1:]

    if path == 'products':
        products = products_table.scan()['Items']
        return {
            'statusCode': 200,
            'body': json.dumps({
                'products': products,
            })
        }

    if path == 'product':
        products = products_table.query(
            IndexName='handle',
            KeyConditionExpression=Key('handle').eq(path_params[0])
        )['Items']
        return {
            'statusCode': 200,
            'body': json.dumps({
                'product': products[0]
            })
        }

    return {
        'statusCode': 400,
        'body': 'You messed up.'
    }
