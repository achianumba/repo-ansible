#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
from pathlib import Path
import yaml
from jsonschema import Draft7Validator, ValidationError

DOCUMENTATION = r'''
module: load_repo

short_description: >-
  Sets `repo` and `repo_extras` facts to dictionaries containing data loaded/inferred from the 
  `repo.yaml` and other metadata files in a project.

options:
  path:
    description: Absolute path to the target repository's root
    type: str
    required: true

author:
  - Arinze Chianumba (@achianumba)
'''

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

    repo_dir = Path(module.params['path'])

    if not repo_dir.is_dir():
        module.fail_json(
            msg=f"Repository directory '{repo_dir}' is inaccessible or doesn't exist."
        )
    
    repo_yaml = repo_dir.joinpath('repo.yaml')

    [ repo_data, original_repo_data ] = load_repo_yaml(repo_yaml, module)
    
    repo_extras = infer_metadata(repo_dir)
    repo_docs_dir = repo_dir.joinpath('docs')
    repo_docs_partials = repo_docs_dir.joinpath('partials')

    repo_extras.update({
        'path': str(repo_dir),
        'file': str(repo_yaml),
        'version': repo_data['version'],
        'notice': 'Managed by https://github.com/linkorb/repo-ansible. Manual changes will be overwritten.',
        'docs_dir': str(repo_docs_dir),
        'docs_partials_dir': str(repo_docs_partials),
        'enable_reviewdog': len(repo_data['reviewdog']['platforms']) > 0
    })

    module.exit_json(
        changed=False,
        ansible_facts={
            'repo': repo_data,
            'repo_extras': repo_extras,
            'original_repo_data': original_repo_data
            }
    )


def load_repo_yaml(repo_yaml, module):
    if not repo_yaml.exists():
        module.fail_json(
            msg=f"'{repo_yaml}' doesn't exist."
        )

    if not repo_yaml.is_file():
        module.fail_json(
            msg=f"'{repo_yaml}' is not a file."
        )

    schema_yaml = Path.cwd().joinpath('repo.schema.yaml')

    with open(repo_yaml, 'r') as file:
        repo_data = yaml.safe_load(file)

    with open(schema_yaml, 'r') as file:
        schema = yaml.safe_load(file)
        defaults = extract_defaults(schema)

    repo_data_with_defaults = deep_update(defaults, repo_data)

    try:
        Draft7Validator(schema).validate(repo_data_with_defaults)
    except ValidationError as err:
        message = f'''
        repo.yaml file is invalid: {err.message}.
        
        Please refer to the reference schema at https://github.com/linkorb/repo-ansible/?tab=readme-ov-file#short-reference-configuration for mor information.
        '''
        module.fail_json(msg=message)

    return [ repo_data_with_defaults, repo_data ]


def extract_defaults(schema_yaml):
    if 'default' in schema_yaml:
        return schema_yaml['default']

    if 'properties' in schema_yaml:
        collect = {}
        for v in schema_yaml['properties']:
            got = extract_defaults(schema_yaml['properties'][v])
            if got is not None:
                collect[v] = got
        return collect if len(collect) else None
    else:
        return None
    

# Function definition copied from pydantic.v1.utils
#
# The MIT License (MIT)
# Copyright (c) 2017 to present Pydantic Services Inc. and individual contributors.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
def deep_update(mapping, *updating_mappings):
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping


def infer_metadata(repo_dir):
    metadata = {
        'is_nodejs': 'package.json',
        'is_php': 'composer.json',
        'is_ansible': 'ansible.cfg',
        'is_python': [
            'requirements.txt', 
            'setup.py',
            'pyproject.toml', # Poetry, Flit, PiP
            'Pipfile', # Pipenv
            'conda.yml', # Conda,
            'pytest.ini', # Pytest
            'setup.cfg', # Pytest
            'ansible.cfg' # Ansible
        ],
        # Docker in docker
        'is_docker': 'Dockerfile',
        'is_compose': [
            'compose.yaml',
            'compose.yml',
            'docker-compose.yml',
            'docker-compose.yaml'
            ],
        'is_make': 'Makefile'
    }

    for fieldName in metadata:
        value = metadata[fieldName]

        if (isinstance(value, list)):
            file_exists = False

            for filename in value:
                if repo_dir.joinpath(filename).is_file():
                    file_exists = True
                    break
            
            metadata[fieldName] = file_exists
            
            continue
        
        if repo_dir.joinpath(value).is_file():
            metadata[fieldName] = True
            continue
        
        metadata[fieldName] = False

    return metadata
    
if __name__ == '__main__':
    main()