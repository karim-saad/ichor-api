'''
Script to populate template.yml file with sensitive environment variables
'''
import json
if __name__ == '__main__':
    empty_template = open('empty_template.yml').read()
    env_vars = json.loads(open('.params.json').read())

    populated_template = empty_template
    populated_template += '\nParameters:\n'
    for env_var in env_vars:
        populated_template += f'  {env_var}:\n'
        populated_template += '    Type: String\n'
        populated_template += f'    Default: {env_vars[env_var]}\n'

    open('template.yml', 'w').write(populated_template)
