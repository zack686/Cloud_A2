#!/bin/bash
. ./unimelb-COMP90024-2022-grp-24-openrc.sh; ansible-playbook nectar.yaml -u ubuntu --ask-become-pass --key-file=~/.ssh/id_rsa