# Inspired and adapted from https://github.com/geerlingguy/ansible-role-test-vms... thanks a lot!

# -*- mode: ruby -*-
# vi: set ft=ruby :
require "json"

VAGRANTFILE_API_VERSION = "2"

# Set to 'true' when testing new base box builds locally.
TEST_MODE = false
LOCAL_BOX_DIRECTORY = "file://~/Downloads/"

# Uncomment when explicitly testing VirtualBox.
PROVIDER_UNDER_TEST = "virtualbox"
NETWORK_PRIVATE_IP_PREFIX = "172.16.3."

# Uncomment when explicitly testing VMWare.
# PROVIDER_UNDER_TEST = "vmware"
# NETWORK_PRIVATE_IP_PREFIX = "192.168.3."

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    # https://www.vagrantup.com/docs/vagrantfile/ssh_settings.html
    config.ssh.insert_key = false
    config.ssh.forward_agent = true
    config.ssh.private_key_path = ["~/.ssh/id_rsa", "~/.vagrant.d/insecure_private_key"]

    # VirtualBox.
    # https://www.vagrantup.com/docs/virtualbox/configuration.html
    config.vm.provider :virtualbox do |v|
        # https://www.vagrantup.com/docs/virtualbox/configuration.html#gui-vs-headless
        if ENV['MULTI_DEV_MACHINE_GUI']
            v.gui = true
        end

        # https://www.vagrantup.com/docs/virtualbox/configuration.html#linked-clones
        v.linked_clone = true

        # https://www.vagrantup.com/docs/virtualbox/configuration.html#vboxmanage-customizations
        v.memory = 1024
        v.cpus = 3
        v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        v.customize ["modifyvm", :id, "--ioapic", "on"]
    end

    # VMware Fusion.
    # https://www.vagrantup.com/docs/vmware/configuration.html
    config.vm.provider :vmware_fusion do |v, override|
        v.vmx["memsize"] = 1024
        v.vmx["numvcpus"] = 3
    end

    # https://www.vagrantup.com/docs/synced-folders/basic_usage.html
    # Replace the default shared folder /vagrant
    config.vm.synced_folder ".", "/home/vagrant/dotfiles"
    # Configure all extra ~/dotfiles_* directories as shared folders
    Dir[File.expand_path('~/dotfiles_*')].each do |dotfile_dir|
        config.vm.synced_folder dotfile_dir, "/home/vagrant/" + File.basename(dotfile_dir)
    end

    # Prepare a dynamic list of Vagrant VMs from a JSON file
    vm_ip = 1
    json_string = open("Vagrantfile.jsonc").read
    parsed_json = JSON.parse(json_string)
    parsed_json["vms"].each do |json_vm|
        vm_name = json_vm["name"]
        vm_box = json_vm["box"]
        vm_box_version = json_vm["box_version"]
        vm_ip += 1

        config.vm.define vm_name do |machine|
            machine.vm.hostname = vm_name + "-virtual-machine"
            if not TEST_MODE
                machine.vm.box = vm_box
            else
                machine.vm.box = LOCAL_BOX_DIRECTORY + PROVIDER_UNDER_TEST + "-" + vm_name + ".box"
            end
            if vm_box_version
                machine.vm.box_version = vm_box_version
            end
            machine.vm.network :private_network, ip: NETWORK_PRIVATE_IP_PREFIX + vm_ip.to_s

            # Ansible Local: https://www.vagrantup.com/docs/provisioning/ansible_local.html
            machine.vm.provision "ansible_local" do |ansible|
                # Common options: https://www.vagrantup.com/docs/provisioning/ansible_common.html
                ansible.compatibility_mode = "2.0"
                ansible.provisioning_path = "/home/vagrant/dotfiles"
                ansible.limit = "all"
                ansible.inventory_path = "hosts"
                ansible.playbook = "local_env.yml"

                verbose = ENV['MULTI_DEV_MACHINE_VERBOSE']
                if verbose
                    ansible.verbose = verbose
                end

                tags = ENV['MULTI_DEV_MACHINE_TAGS']
                if tags
                    ansible.tags = tags
                end
            end
        end
    end
end
