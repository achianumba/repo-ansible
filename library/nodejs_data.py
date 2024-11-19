#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule

from pathlib import Path
from json import loads as loadJson

DOCUMENTATION = r'''
module: nodejs_data

short_description: >-
    Sets a `nodejs_data` dictionary containing data inferred from the NodeJS-specific metadata
    of a project.

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

    lock_files = ['package-lock.json', 'pnpm-lock.yaml', 'yarn.lock']
    metadata = {
        'is_npm': 'package-lock.json',
        'is_pnpm': 'pnpm-lock.yaml',
        'is_yarn': 'yarn.lock',
        'lock_file': '',
        'is_puppeteer': ''
    }


    for field_name in metadata:
        if field_name in ['lock_file', 'is_puppeteer']:
            continue

        filename = metadata[field_name]

        if repo_dir.joinpath(filename).is_file():
            metadata[field_name] = True
            
            if filename in lock_files:
                metadata['lock_file'] = str(repo_dir.joinpath(filename))
            continue
        
        metadata[field_name] = False
    
    # TODO: Handling non-existing lock file
    with open(metadata['lock_file']) as lock_file_contents:
        if 'puppeteer' in lock_file_contents.read():
            metadata['is_puppeteer'] = True

    # TODO: Determine if compose is required for db
    db_packages = {
        'postgres': ['pg', 'pg-native', 'pg-promise', 'node-postgres'],
        'mysql': ['mysql', 'mysql2'],
        'mariadb': '',
        'sqlite3': ['sqlite3', 'better-sqlite3'],
        'mongodb': ['mongodb','mongoose'],
        'redis': '',
        'couchbase': '',
        'firebase': ['firebase','@firebase'],
        'sequelize': '',
        'typeorm': '',
        'prisma': '',
        'objection': '',
        'knex': '',
        'bookshelf': '',
        '@aws-sdk/client-dynamodb': ['@aws-sdk/client-dynamodb', 'dynamodb-toolbox'], #amazon/dynamodb-local
        'firebase': ['firebase', '@google-cloud/firestore'],
        '@azure/cosmos': ['@azure/cosmos'] # mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest
        }

    module.exit_json(ansible_facts={'nodejs_data': metadata })

if __name__ == '__main__':
    main()