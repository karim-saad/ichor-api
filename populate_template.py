'''
Script to populate template.yml file with sensitive environment variables
'''
import json


if __name__ == '__main__':
    with open('empty_template.yml') as f:
        empty_template = f.read()
    with open('params.json') as f:
        env_vars = json.loads(f.read())

    populated_template = empty_template + '\nParameters:\n'
    for key, value in env_vars.items():
        populated_template += f'  {key}:\n'
        populated_template += '    Type: String\n'
        populated_template += f'    Default: {value}\n'

    with open('template.yml', 'w') as f:
        f.write(populated_template)
