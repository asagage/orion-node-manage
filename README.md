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

    - hosts: all
      roles:
         - { role: asagage.orion-node-manage }
      tasks:
        - name: Unmanage node
          local_action:
            module: orion_node_manage
            ip_address: hostvars[inventory_hostname]['ansible_default_ipv4']['address']
            state: unmanaged
        
        - name: Remanage node
          local_action:
            module: orion_node_manage
            ip_address: hostvars[inventory_hostname]['ansible_default_ipv4']['address']
            state: managed
   

License
-------

BSD

Author Information
------------------

Asa Gage @asagage