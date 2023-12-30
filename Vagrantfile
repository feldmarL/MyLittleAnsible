# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  $password_script = <<-EOF
  apt update
  apt install -y openssh-server
  useradd -m -s /bin/bash mla
  echo -e "password_mla\npassword_mla" | passwd mla
  usermod -aG sudo mla
  EOF

  $ssh_script = <<-EOF
  mkdir -p /home/mla/.ssh
  mv /tmp/mla_key.pub /home/mla/.ssh/mla_key.pub
  cat /home/mla/.ssh/mla_key.pub >> /home/mla/.ssh/authorized_keys
  chown -R mla:mla /home/mla/.ssh
  sed -i '58s/no/yes/' /etc/ssh/sshd_config
  systemctl restart sshd
  EOF

  config.vm.box                 = "debian/bullseye64"
  config.vm.box_check_update    = false

  config.vm.provision "shell", inline: $password_script
  config.vm.provision "file", source: "./mla_key.pub", destination: "/tmp/mla_key.pub"
  config.vm.provision "shell", inline: $ssh_script

  config.vm.define "server-1" do |server|

    server.vm.hostname          = "server-1"

    server.vm.provider :virtualbox do |machine|
      machine.name    = "server-1"
      machine.memory  = 1024
      machine.cpus    = 1
    end
  end

  config.vm.define "server-2" do |server|

    server.vm.hostname          = "server-2"

    server.vm.provider :virtualbox do |machine|
      machine.name    = "server-2"
      machine.memory  = 1024
      machine.cpus    = 1
    end
  end
end
