#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
from pathlib import Path

DOCUMENTATION = r'''
module: load_docs

short_description: |
  Sets facts for the following docs related tasks

  - Partials generation

options:
  path:
    description: An absolute path to the repository's ***docs/*** folder
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

    docs_dir = Path(module.params['path'])
    partials_dir = docs_dir.joinpath('partials')
    facts = { 'docs_partials': {} }

    if not docs_dir.exists() or not partials_dir.exists():
        module.exit_json(changed=False, ansible_facts=facts)

    for path in partials_dir.glob('readme.*.md'):
        facts['docs_partials'][path.stem[7:]] = path.read_text()

    module.exit_json(changed=False, ansible_facts=facts)
    
if __name__ == '__main__':
    main()