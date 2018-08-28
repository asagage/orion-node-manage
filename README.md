orion-node-manage
=========

This role provides the orion_node_manage module for Unmanaging and Remanaging Nodes in Orion. It can be used to suppress alerts during maintenance of Orion managed systems.
For more info please see the module file located in ./library/orion_node_manage.py.

Requirements
------------

This module will install all pip packages needed by the module.


Example Playbook
----------------

I recommend running this on the local node as follows:

    - name: Setup Local Solarwinds
      hosts: localhost
      gather_facts: no
      roles:
          - { role: asagage.orion-node-manage }

    - name: Solarwinds Manage Nodes
      hosts: all
      tasks:
        - name: Unmanage node via IP Address
          local_action:
            module: orion_node_manage
            ip_address: hostvars[inventory_hostname]['ansible_default_ipv4']['address']
            state: unmanaged
            username: "{{ sw_username }}"
            password: "{{ sw_password }}"
            hostname: "{{ sw_hostname }}"

        - name: Unmanage node via DNS Name
          local_action:
            module: orion_node_manage
            dns_name: "{{inventory_hostname}}"
            state: unmanaged
            username: "{{ sw_username }}"
            password: "{{ sw_password }}"
            hostname: "{{ sw_hostname }}"

        - name: Remanage node via IP Address
          local_action:
            module: orion_node_manage
            ip_address: hostvars[inventory_hostname]['ansible_default_ipv4']['address']
            state: managed
            username: "{{ sw_username }}"
            password: "{{ sw_password }}"
            hostname: "{{ sw_hostname }}"

        - name: Remanage node via DNS Name
          local_action:
            module: orion_node_manage
            dns_name: "{{inventory_hostname}}"
            state: managed
            username: "{{ sw_username }}"
            password: "{{ sw_password }}"
            hostname: "{{ sw_hostname }}"

License
-------

MIT

Author Information
------------------

Asa Gage @asagage
