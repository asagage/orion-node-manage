#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2018, Asa Gage <asagage@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pandas as pd

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: orion_node_manage
short_description: Unmanages/Remanages Orion Nodes
description:
- "Unmanage/Remanage nodes within Orion"
version_added: "2.0"
author: "Asa Gage (@asagage)"
requirements:
    - orionsdk
    - datetime
    - requests
    - pandas
    - traceback
options:
    hostname:
        description:
            - Your Orion instance hostname.
        required: true
    username:
        description:
            - Your Orion username.
            - Note: Active Directory users must use DOMAIN\\username format to avoid 403 errors.
        required: true
    password:
        description:
            - Your Orion password.
        required: true
    state:
        description:
            - The designated state of the node.
        required: true
        choices:
            - managed
            - unmanaged
    node_id:
        description:
            - The NodeID of the node to remanage/unmanage.
            - Must provide either a node_id or an ip_address.
        required: false
    ip_address:
        description:
            - The ip address of the node to remanage/unmanage.
            - Must provide either a node_id or an ip_address.
        required: false
    dns_name:
        description:
            - The DNS name of the node to remanage/unmanage.
            - Must provide either a node_id or an ip_address.
    unmanage_from:
        description:
            - The date and time (in ISO 8601 UTC format) to begin the unmanage period.
            - If this is in the past, the node will be unmanaged effective immediately.
            - If not provided, module defaults to now.
            - ex: "2017-02-21T12:00:00Z"
        required: false
    unmanage_until:
        description:
            - The date and time (in ISO 8601 UTC format) to end the unmanage period.
            - You can set this as far in the future as you like.
            - If not provided, module defaults to 24 hours from now.
            - ex: "2017-02-21T12:00:00Z"
        required: false
    is_relative:
        description:
            - If true, then the unmanage_until argument will be interpreted differently:
            - The date portion will be ignored and the time portion will be treated as a duration.
        required: false
        default: 'no'
'''

EXAMPLES = '''
# Unmanage a node
- orion_node_manage:
    node_id: "123"
    state: "unmanaged"
    unmanage_until: "2017-02-21T12:00:00Z"
    hostname: "localhost"
    username: "username"
    password: "password"

# Remanage a node
- orion_node_manage:
    node_id: "123"
    state: "managed"
    hostname: "localhost"
    username: "username"
    password: "password"

'''
import traceback

# Import OrionSDK
try:
    from orionsdk import SwisClient
    HAS_ORION = True
except:
    HAS_ORION = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native

import requests
from datetime import datetime, timedelta

__SWIS__ = None
requests.packages.urllib3.disable_warnings()

def main():
    global __SWIS__
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            state=dict(required=True, choices=['managed', 'unmanaged']),
            node_id=dict(required=False),
            ip_address=dict(required=False),
            dns_name=dict(required=False),
            unmanage_from=dict(required=False, default=None),
            unmanage_until=dict(required=False, default=None),
            is_relative=dict(required=False, default=False, type='bool')
        )
    )

    # Prepare Orion
    if not HAS_ORION:
        module.fail_json(msg='orionsdk required for this module')

    options = {
        'hostname': module.params['hostname'],
        'username': module.params['username'],
        'password': module.params['password']
    }

    __SWIS__ = SwisClient(**options)

    try:
        __SWIS__.query('SELECT Uri FROM Orion.Environment')
    except Exception as e:
        module.fail_json(msg="Failed to query Orion. Check Hostname, Username, and Password : {0}".format(str(e)))

    if module.params['state'] == 'managed':
        remanage_node(module)
    elif module.params['state'] == 'unmanaged':
        unmanage_node(module)

def _get_node(module):
    node = {}
    if module.params['node_id'] is not None:
        # search for node
        results = __SWIS__.query(
            'SELECT NodeID, Caption, Unmanaged, UnManageFrom, UnManageUntil FROM Orion.Nodes WHERE NodeID = '
            '@node_id',
            node_id = module.params['node_id'])

    elif module.params['ip_address'] is not None:
        # search for IP
        results = __SWIS__.query(
            'SELECT NodeID, Caption, Unmanaged, UnManageFrom, UnManageUntil FROM Orion.Nodes WHERE IPAddress = '
            '@ip_addr',
            ip_addr = module.params['ip_address'])

    elif module.params['dns_name'] is not None:
        # search for DNS Name
        results = __SWIS__.query(
            'SELECT NodeID, Caption, Unmanaged, UnManageFrom, UnManageUntil FROM Orion.Nodes WHERE DNS = '
            '@dns_name',
            dns_name = module.params['dns_name'])

    else:
        # no id provided
        module.fail_json(msg="You must provide either node_id, IP Address, or DNS Name")

    if results['results']:
        node['nodeId'] = results['results'][0]['NodeID']
        node['caption'] = results['results'][0]['Caption']
        node['netObjectId'] = 'N:{}'.format(node['nodeId'])
        node['unmanaged'] = results['results'][0]['Unmanaged']
        node['unManageFrom'] = str(pd.to_datetime(results['results'][0]['UnManageFrom']).isoformat())
        node['unManageUntil'] = str(pd.to_datetime(results['results'][0]['UnManageUntil']).isoformat())
    return node

def remanage_node(module):
    node = _get_node(module)
    if not node:
        module.fail_json(msg="Monitor not found!")
    elif (node['unmanaged'] == False):
        module.exit_json(changed=False)
    try:
        __SWIS__.invoke('Orion.Nodes', 'Remanage', node['netObjectId'])
        module.exit_json(changed=True, msg="{0} has been remanaged".format(node['caption']))
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())

def unmanage_node(module):
    now = datetime.utcnow()
    tomorrow = now + timedelta(days=1)

    node = _get_node(module)

    unmanage_from = module.params['unmanage_from']
    unmanage_until = module.params['unmanage_until']

    is_relative = module.params['is_relative']

    if not unmanage_from:
        unmanage_from = now

    if not unmanage_until:
        unmanage_until = tomorrow

    if not node:
        module.fail_json(msg="Monitor not found!")
    elif (node['unmanaged'] == True):
        if(unmanage_from == node['unManageFrom']) and (unmanage_until == node['unManageUntil']):
            module.exit_json(changed=False)
    try:
        __SWIS__.invoke('Orion.Nodes', 'Unmanage', node['netObjectId'], unmanage_from, unmanage_until, is_relative)
        msg = "{0} will be unmanaged from {1} until {2}".format(node['caption'], unmanage_from, unmanage_until)
        module.exit_json(changed=True, msg=msg)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())

if __name__ == '__main__':
    main()
