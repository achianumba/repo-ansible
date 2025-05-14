#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
from pathlib import Path


DOCUMENTATION = r'''
  module: list_extension_workflows

  short_description: Sets a dictionary of extension workflows as `extension_workflows`
    
    
options:
  prefix:
    description: Absolute path to the target repository's GitHub workflows folder
    type: str
    required: true

author:
  - Marius Ghita (@mhitza)
  - Arinze Chianumba (@achianumba)
'''

def main():
    argument_spec = {
        'prefix': {
            'type': str,
            'required': True
        }
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    workflows_dir = Path(module.params['prefix'])
    workflows_relative_dir = Path('.github').joinpath('workflows')
    workflow_files = workflows_dir.glob('[0-9][0-9]-*.yaml')
    file_buckets = {}

    for path in workflow_files:
        filename = path.name
        workflow_prefix = filename[:2]

        if (int(workflow_prefix) % 10) == 0:
            continue
        
        bucket = workflow_prefix + '0'
        
        if bucket not in file_buckets:
          file_buckets[bucket] = []
        
        file_buckets[bucket].append({
           'name': filename,
           'path_from_root': str(workflows_relative_dir.joinpath(filename))
        })


    module.exit_json(changed=False, ansible_facts={'extension_workflows': file_buckets })

if __name__ == '__main__':
  main()
