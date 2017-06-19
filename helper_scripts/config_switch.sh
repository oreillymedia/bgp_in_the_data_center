#!/bin/bash

#This file is transferred to the Cumulus VX and executed to re-map interfaces
#Extra config COULD be added here but I would recommend against that to keep this file standard.
echo "#################################"
echo "  Running Switch Post Config"
echo "#################################"
sudo su

echo "  adding fake cl-acltool..."
echo -e "#!/bin/bash\nexit 0" > /bin/cl-acltool
chmod 755 /bin/cl-acltool

cat <<EOF > /etc/network/interfaces
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5), ifup(8)
#
# Please see /usr/share/doc/python-ifupdown2/examples/ for examples
#
#

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
auto eth0
iface eth0 inet dhcp
EOF

## Convenience code. This is normally done in ZTP.
echo "cumulus ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/10_cumulus
mkdir -p /home/cumulus/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCzH+R+UhjVicUtI0daNUcedYhfvgT1dbZXgY33Ibm4MOo+X84Iwuzirm3QFnYf2O3uyZjNyrA6fj9qFE7Ekul4bD6PCstQupXPwfPMjns2M7tkHsKnLYjNxWNql/rCUxoH2B6nPyztcRCass3lIc2clfXkCY9Jtf7kgC2e/dmchywPV5PrFqtlHgZUnyoPyWBH7OjPLVxYwtCJn96sFkrjaG9QDOeoeiNvcGlk4DJp/g9L4f2AaEq69x8+gBTFUqAFsD8ecO941cM8sa1167rsRPx7SK3270Ji5EUF3lZsgpaiIgMhtIB/7QNTkN9ZjQBazxxlNVN6WthF8okb7OSt" >> /home/cumulus/.ssh/authorized_keys
chmod 700 -R /home/cumulus/.ssh
chown cumulus:cumulus -R /home/cumulus/.ssh
echo "This is a fake license" > /etc/cumulus/.license.txt

## Make onie reinstalls work. Note that installing from onie will undo these changes.
mkdir /tmp/foo
mount LABEL=ONIE-BOOT /tmp/foo
sed -i 's/eth0/eth1/g' /tmp/foo/grub/grub.cfg
sed -i 's/eth0/eth1/g' /tmp/foo/onie/grub/grub-extra.cfg
umount /tmp/foo



echo "#################################"
echo "   Finished"
echo "#################################"
