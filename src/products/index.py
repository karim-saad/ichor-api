from json import dumps


def handler(event, context):
    test_return = {
        'test-param-1': 'yes',
        'test-param-2': 'no'
    }
    return {
        'statusCode': 200,
        'body': dumps(test_return)
    }
