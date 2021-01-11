# instance_esx_vm_with_Terraform
Templates creation to feed Terraform ESX provider before creating CentOS VM


Prerequisites :

- An ESX with SSH allowed
- Terraform with this provider : https://github.com/josenk/terraform-provider-esxi
- The VM to copy with cloud-init installed and this utility :
curl -sSL https://raw.githubusercontent.com/vmware/cloud-init-vmware-guestinfo/master/install.sh | sh -
- IP Address of the VM is set in the DNS (VM is created with static IP)


Interface expects to be named "eth0", so before copy the source image :
 yum install -y network-scripts  
 echo 'NM_CONTROLLED="no"'  >> /etc/sysconfig/network-scripts/ifcfg-eth0  
 sed  -i 's/NAME=".*"/NAME="eth0"/g' /etc/sysconfig/network-scripts/ifcfg-eth0  
 sed  -i 's/DEVICE=".*"/DEVICE="eth0"/g' /etc/sysconfig/network-scripts/ifcfg-eth0  
 # Disable NetworkManager
 # https://access.redhat.com/solutions/4365931
 touch /etc/sysconfig/disable-deprecation-warnings  
 systemctl stop NetworkManager  
 systemctl disable NetworkManager  
 systemctl enable network  
 sed -i 's/rhgb/net.ifnames=0 rhgb/g' /etc/default/grub  
 grub2-mkconfig  -o /boot/grub2/grub.cfg  


Variables have to be changed :
In instance_vm_with.py :
 - dns1, dns2, domain and gateway

In templates/userdata.template :
 - source image password and if you've planned to use Ansible directly after instanciation : the username wich Ansibles uses to connect, the ssh key, the ansible user and the ansible server

