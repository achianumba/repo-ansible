#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
from pathlib import Path
import yaml

DOCUMENTATION = r'''
module: yaml_format

short_description: Formats a YAML file

options:
  path:
    description: Absolute path to the yaml file to be formatted
    type: str
    required: true

author:
  - Marius Ghita (@mhitza)
  - Arinze Chianumba (@achianumba)
'''

# https://stackoverflow.com/questions/45004464/yaml-dump-adding-unwanted-newlines-in-multiline-strings
yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str

# Represent strings as multiline within YAML file, if the string contains the newline character
def repr_str(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
    return dumper.org_represent_str(data)


yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)

def main():
    argument_spec = {
        'path': {
            'type': str,
            'required': True
        }
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    file_path = Path(module.params['path'])

    with open(file_path, 'r') as file:
        document = file.read()

    structure = yaml.safe_load(document)
    
    with open(file_path, 'w') as file:
        yaml.safe_dump(structure, file)
    
    module.exit_json(
        changed=True
    )

if __name__ == '__main__':
    main()