#!/bin/sh
sudo sh -c 'echo "deb http://httpredir.debian.org/debian jessie main" > /etc/apt/sources.list.d/jessie.list'
sudo sh -c 'echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list.d/jessie.list'
sudo sh -c 'echo "deb http://repo3.cumulusnetworks.com/repo Jessie-supplemental upstream" > /etc/apt/sources.list.d/jessie_cl.list'
sudo apt-get update
sudo apt-get install -yq git python-netaddr
sudo apt-get install -yq -t jessie-backports ansible
git clone https://github.com/CumulusNetworks/cldemo-provision-ts.git
