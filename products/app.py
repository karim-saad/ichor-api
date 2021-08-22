'''
Entry file for products Lambda
'''
import json

import boto3
from boto3.dynamodb.conditions import Key


def handler(event, _context):
    '''
    Products lambda function
    '''
    query_params = event['queryStringParameters']
    products = get_product_by_handle(
        query_params['handle']) if query_params else get_all_products()
    return {
        'statusCode': 200,
        'body': json.dumps({
            'products': products
        })
    }


def get_product_by_handle(handle):
    '''
    Get specific products that match on handle
    '''
    products_table = boto3.resource('dynamodb').Table('products')
    return products_table.query(
        IndexName='handle',
        KeyConditionExpression=Key('handle').eq(handle)
    )['Items']


def get_all_products():
    '''
    Get all products
    '''
    products_table = boto3.resource('dynamodb').Table('products')
    return products_table.scan()['Items']
