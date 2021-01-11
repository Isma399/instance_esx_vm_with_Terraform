#!/usr/bin/python
# Terraform + esxi Provider
# Instance this VM
# Wait for an IP, name, virtual network and esx datastore
# DISK, RAM and CPU is taken from the clone.
# virtual_network is VLAN15 by default
# Default datastore is "IMAGES"

from jinja2 import Environment
from jinja2 import FileSystemLoader
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
import os
import sys
from subprocess import Popen, PIPE
import shutil
import socket


dns1 = "8.8.8.8"
dns2 = "8.8.4.4"
domain = "example.com"
gateway = "0.0.0.0"

def parse_args():
    parser = ArgumentParser(
        description='Instance VM with Terraform + esxi Provider.',
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--name",
                        dest="vm_hostname",
                        help="vm_hostname")
    parser.add_argument("--network",
                        dest="virtual_network",
                        default="VLAN15",
                        help="Virtual Network")
    parser.add_argument("--datastore",
                        dest="datastore",
                        default="IMAGES",
                        help="ESX datastore")
    parser.add_argument("--esx",
                        dest="esx",
                        help="ESX IP address or hostname")
    parser.add_argument("--esx-admin-password", "-p",
                        dest="password",
                       help="Admin password for esx") 
    p = parser.parse_args()
    ip_address = socket.gethostbyname(p.vm_hostname)
    return ip_address, p.vm_hostname, p.virtual_network, p.datastore, p.esx, p.password


def create_folder(vm_hostname):
    try:
        os.makedirs('./vms/' + vm_hostname)
        return os.getcwd() + '/vms/' + vm_hostname
    except OSError as e:
        print e
        sys.exit(1)


def give_template(filename):
    template_loader = FileSystemLoader(searchpath="./templates/")
    template_env = Environment(loader=template_loader)
    TEMPLATE_FILE = filename
    return template_env.get_template(TEMPLATE_FILE)


def create_network_config(ip_address, netmask, gateway, dns1, dns2, domain):
    template = give_template("network_config.template")
    output_text = template.render(ip_address=ip_address,
                                  gateway=gateway,
                                  dns1=dns1,
                                  dn2=dns2,
                                  domain=domain)
    return output_text


def create_metadata(folder, vm_hostname):
    command = 'gzip -c9 <' + folder + '/network.config.yaml | base64 -w0'
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    network_config = p.stdout.read()
    template = give_template("metadata.template")
    output_text = template.render(network_yaml=network_config,
                                  vm_hostname=vm_hostname)
    return output_text


def create_main_tf(ip_address, vm_hostname, virtual_network, datastore, esx, password):
    template = give_template("main.template")
    gateway = '.'.join(ip_address.split('.')[0:3]) + '.18'
    output_text = template.render(ip_address=ip_address,
                                  vm_hostname=vm_hostname,
                                  virtual_network=virtual_network,
                                  datastore=datastore,
                                  esx=esx,
                                  gateway=gateway,
                                  password=password)
    return output_text


def instance(folder):
    print 'chdir ' + folder
    os.chdir(folder)
    p = Popen('terraform init -input=false', shell=True, stdout=PIPE, stderr=PIPE)
    print p.stdout.read()
    p = Popen('terraform apply -input=false -auto-approve', shell=True, stdout=PIPE, stderr=PIPE)
    print p.stdout.read()


def delete_from_knowhosts(vm_hostname):
    p = Popen('ssh-keygen -R ' + vm_hostname, shell=True, stdout=PIPE, stderr=PIPE)
    print p.stdout.read()


if __name__ == '__main__':
    ip_address, vm_hostname, virtual_network, datastore, esx, password = parse_args()

    folder = create_folder(vm_hostname)

    network_yaml = create_network_config(ip_address)
    # gzip -c9 <network.config.yaml | base64 -w0
    with open(folder + '/network.config.yaml', 'w') as f:
        f.write(network_yaml)
    metadata = create_metadata(folder, vm_hostname)
    with open(folder + '/metadata.json', 'w') as f:
        f.write(metadata)

    main_tf = create_main_tf(ip_address, vm_hostname, virtual_network,
                             datastore, esx, password)
    with open(folder + '/main.tf', 'w') as f:
        f.write(main_tf)
    print 'Writes ' + folder
    shutil.copyfile('./templates/userdata.template', folder + '/userdata.tpl')

    delete_from_knowhosts(vm_hostname)
    #instance(folder) # Not working

