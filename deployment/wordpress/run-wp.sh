#!/bin/bash

ansible-playbook -i hosts -u ubuntu --key-file=keys/group24_key.pem wordpress.yaml