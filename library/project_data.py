#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule

from pathlib import Path

DOCUMENTATION = r'''
module: project_data

short_description: >-
    Sets a `project_data` dictionary containing information that inferred from
    the metadata files in a project.

options:
    repo_dir:
        type: string
        required: true
        description: Absolute path to the target repository's root.

author:
  - Arinze Chianumba (@achianumba)
'''

def main():
    module_args = {
        'repo_dir': {
            type: 'str',
            'required': True
        }
    }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    repo_dir = Path(module.params['repo_dir'])

    if not repo_dir.is_dir():
        module.fail_json(
            msg=f"Repository directory '{repo_dir}' is inaccessible or doesn't exist."
        )
    
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

    module.exit_json(ansible_facts={'project_data': metadata })

if __name__ == '__main__':
    main()