#!/bin/bash

#This file is transferred to a Debian/Ubuntu Host and executed to re-map interfaces
#Extra config COULD be added here but I would recommend against that to keep this file standard.
echo "#################################"
echo "  Running Server Post Config"
echo "#################################"
sudo su



useradd cumulus
CUMULUS_HASH=`python -c 'import crypt; print(crypt.crypt("CumulusLinux!", "\$6\$saltsalt\$").replace("/","\\/"))'`
sed "s/cumulus:!/cumulus:$CUMULUS_HASH/" -i /etc/shadow
mkdir -p /home/cumulus/
sed "s/PasswordAuthentication no/PasswordAuthentication yes/" -i /etc/ssh/sshd_config
chsh -s /bin/bash cumulus

## Convenience code. This is normally done in ZTP.
echo "cumulus ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/10_cumulus
mkdir -p /home/cumulus/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCzH+R+UhjVicUtI0daNUcedYhfvgT1dbZXgY33Ibm4MOo+X84Iwuzirm3QFnYf2O3uyZjNyrA6fj9qFE7Ekul4bD6PCstQupXPwfPMjns2M7tkHsKnLYjNxWNql/rCUxoH2B6nPyztcRCass3lIc2clfXkCY9Jtf7kgC2e/dmchywPV5PrFqtlHgZUnyoPyWBH7OjPLVxYwtCJn96sFkrjaG9QDOeoeiNvcGlk4DJp/g9L4f2AaEq69x8+gBTFUqAFsD8ecO941cM8sa1167rsRPx7SK3270Ji5EUF3lZsgpaiIgMhtIB/7QNTkN9ZjQBazxxlNVN6WthF8okb7OSt" >> /home/cumulus/.ssh/authorized_keys
chmod 700 -R /home/cumulus
chown cumulus:cumulus -R /home/cumulus

systemctl disable NetworkManager.service
systemctl stop NetworkManager.service

rm /etc/sysconfig/network-scripts/ifcfg-eth0
echo 'DEVICE="mgmt" BOOTPROTO="dhcp" ONBOOT="yes" TYPE="Ethernet" PERSISTENT_DHCLIENT="yes"' > /etc/sysconfig/network-scripts/ifcfg-mgmt

echo "#################################"
echo "   Finished"
echo "#################################"
