#!/usr/bin/python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licens)

DOCUMENTATION = '''
---
module: apache2_site
version_added: 1.9
author: "Fabrizio Furnari (fabfurnari)"
short_description: enables/disables a site of the Apache2 webserver
description:
   - Enables or disables a specified site of the Apache2 webserver. The module is a very simple copy of the core B(apache2_module) module.
options:
   name:
     description:
       - name of the site to enable/disable
     required: true
   state:
     description:
       - indicate the desired state of the resource
     choices: ['present', 'absent']
     default: present
   purge:
     description:
      - when disabling a site, purge all traces of the site in the internal state data base
requirements: ["a2ensite","a2dissite"]
'''

EXAMPLES = '''
# enables the Apache2 site "default"
- apache2_site: state=present name=default-ssl
# disables the Apache2 site "default"
- apache2_site: state=absent name=default-ssl purge=yes
'''

import re

def _disable_site(module):
    name = module.params['name']
    a2dissite_binary = module.get_bin_path("a2dissite")
    if a2dissite_binary is None:
        module.fail_json(msg="a2dissite not found.  Perhaps this system does not use a2dissite to manage apache")

    purge = '--purge' if module.params['purge'] else ''
    cmd = "{} {} {}".format(a2dissite_binary, purge, name)
    result, stdout, stderr = module.run_command(cmd)

    if re.match(r'.*already disabled', stdout, re.S|re.M):
        module.exit_json(changed = False, result = "Success")
    elif result != 0:
        module.fail_json(msg="Failed to disable site %s: %s" % (name, stdout))
    else:
        module.exit_json(changed = True, result = "Disabled")

def _enable_site(module):
    name = module.params['name']
    a2ensite_binary = module.get_bin_path("a2ensite")
    if a2ensite_binary is None:
        module.fail_json(msg="a2ensite not found.  Perhaps this system does not use a2ensite to manage apache")

    result, stdout, stderr = module.run_command("%s %s" % (a2ensite_binary, name))

    if re.match(r'.*already enabled', stdout, re.S|re.M):
        module.exit_json(changed = False, result = "Success")
    elif result != 0:
        module.fail_json(msg="Failed to enable site %s: %s" % (name, stdout))
    else:
        module.exit_json(changed = True, result = stdout)

def main():
    module = AnsibleModule(
        argument_spec = dict(
            name  = dict(required=True),
            state = dict(default='present', choices=['absent', 'present']),
            purge = dict(default=None, required=False, type='bool')
        ),
    )

    if module.params['state'] == 'present':
        _enable_site(module)

    if module.params['state'] == 'absent':
        _disable_site(module)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
