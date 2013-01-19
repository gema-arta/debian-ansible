# (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

#############################################

import subprocess
import ansible.constants as C
from ansible.inventory.host import Host
from ansible.inventory.group import Group
from ansible import utils
from ansible import errors

class InventoryScript(object):
    ''' Host inventory parser for ansible using external inventory scripts. '''

    def __init__(self, filename=C.DEFAULT_HOST_LIST):

        cmd = [ filename, "--list" ]
        try:
            sp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError, e:
            raise errors.AnsibleError("problem running %s (%s)" % (' '.join(cmd), e))
        (stdout, stderr) = sp.communicate()
        self.data = stdout
        self.groups = self._parse()

    def _parse(self):
        all_hosts = {}

        self.raw = utils.parse_json(self.data)
        all=Group('all')
        groups = dict(all=all)
        group = None
        for (group_name, hosts) in self.raw.items():
            group = groups[group_name] = Group(group_name)
            host = None
            for hostname in hosts:
                if not hostname in all_hosts:
                    all_hosts[hostname] = Host(hostname)
                host = all_hosts[hostname]
                group.add_host(host)
                # FIXME: hack shouldn't be needed
                all.add_host(host)
            all.add_child_group(group)
        return groups
