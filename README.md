BGP in the Data Center
==========

This is the example code that accompanies BGP in the Data Center by Dinesh G. Dutt (ISBN). 

Click the Download Zip button to the right to download example code.

Visit the catalog page [here](http://shop.oreilly.com/product/0636920070467.do).

See an error? Report it [here](http://oreilly.com/catalog/errata.csp?isbn=0636920070467, or simply fork and send us a pull request.


Pre-requisites
----------------

To run the software in this repository, you'll need both [Vagrant](https://www.vagrantup.com/) and [Virtualbox](https://www.virtualbox.org/).
If you're merely interested in looking at the configs, then look under the localconfig directory.

While the book talked about FRRouting as the open source routing suite, because the demo here is based off of Cumulus Linux' 3.3.x release, Quagga is still used. However, the next release of Cumulus Linux will have FRRouting as the default routing suite. That said, the configuration is the same in both cases.

The Quagga version is based off of a Cumulus Linux branch rather than the publicly available version due to the features such as BGP Unnumbered which are present in FRRouting, but not in the public Quagga version.

Topology
---------
![Cumulus Reference Topology](https://github.com/CumulusNetworks/cldemo-vagrant/raw/master/cldemo_topology.png)

Quickstart
-------------
* Install git on your platform if you want to git clone this repository. Else select the download ZIP option from the directory and download the zip file.
* If you're only interested in the configs, look under the localconfig directory.
* If you wish to run this setup please note that running this simulation uses more than 8G of RAM.
* Install [Vagrant](https://releases.hashicorp.com/vagrant/). Use release 1.9.5.
* Install cumulus plugin for vagrant via `vagrant plugin install vagrant-cumulus`
* Install [Ansible](instructions at http://docs.ansible.com/ansible/intro_installation.html)
* If using a zip file, extract the downloaded zip file. If using git, run `git clone git@github.com:oreillymedia/bgp_in_the_data_center.git'
* `cd bgp_in_the_data_center`
* `vagrant up`
* `vagrant ssh oob-mgmt-server`
* `sudo su - cumulus`
* `cd bgp_conf`
* `ansible-playbook -s RUNME.yml`


Details
------------------------

This demo will configure a layer 3 BGP network. The demo is downloaded onto the `oob-mgmt-server` under the `cumulus` user. It assumes the network is up and running (via `vagrant up`) but it **has not** yet been configured. The playbook `RUNME.yml` will configure BGP on all spine and leafs as well as configure the hosts.



Resetting The Topology
------------------------
If a previous configuration was applied to the reference topology, it can be reset with the `reset.yml` playbook provided. This can be run before configuring netq to ensure a clean starting state.

    ansible-playbook -s reset.yml
