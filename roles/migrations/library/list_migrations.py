#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
from pathlib import Path

DOCUMENTATION = r'''
module: list_migrations

short_description: >-
  Sets a `repo_ansible_migrations` fact to a list of required migrations

options:
  version:
    description: version
    type: str
    required: true

author:
  - Marius Ghita (@mhitza)
  - Arinze Chianumba (@achianumba)
'''

def main():
    argument_spec = {
        'version': {
            'type': str,
            'required': True
        }
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    migrations_dir = Path.cwd().joinpath('roles/migrations/tasks')

    available_migrations = list(migrations_dir.glob("migration-v[0-9]*.[0-9]*.[0-9]*.yaml"))
    current_version = module.params['version']
    required_migrations = []

    for path in available_migrations:
        if not path.is_file():
            continue
        
        target_version = path.name[11:-5]

        if should_migrate(current_version, target_version):
            required_migrations.append(str(path))

    module.exit_json(
        changed=False,
        ansible_facts={'repo_ansible_migrations': required_migrations }
    )

def should_migrate(current, target):
    current_version = [int(i) for i in current.split('.')[1:]]
    target_version = [int(i) for i in target.split('.')]
    
    if target_version[0] > current_version[0]:
        return True
    elif target_version[0] < current_version[0]:
        return False

    if target_version[1] > current_version[1]:
        return True
    elif target_version[1] < current_version[1]:
        return False

    if target_version[2] > current_version[2]:
        return True
    elif target_version[2] < current_version[2]:
        return False

    # Returns true when versions are equal. This allows us to pin a migration to an existing
    # version (latest), instead of having to guess the next version number when writing a
    # repo-ansible migration file.
    return True
    
if __name__ == '__main__':
    main()