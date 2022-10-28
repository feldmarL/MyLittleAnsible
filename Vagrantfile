# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  $script = <<-EOF
  apt update && apt install -y openssh-server
  useradd -m -s /bin/bash mla
  echo -e "password_mla\npassword_mla" | passwd mla
  usermod -aG sudo mla
  EOF

  config.vm.define "server-1" do |node|

    node.vm.box               = "debian/bullseye64"
    node.vm.box_check_update  = false
    node.vm.hostname          = "server-1"

    node.vm.provider :virtualbox do |v|
      v.name    = "server-1"
      v.memory  = 1024
      v.cpus    = 1
    end

    node.vm.provision "shell", inline: $script
    node.vm.provision "file", source: "./mla_key.pub", destination: "/tmp/mla_key.pub"
    node.vm.provision "shell", inline: "mkdir -p /home/mla/.ssh \
      && mv /tmp/mla_key.pub /home/mla/.ssh/mla_key.pub \
      && cat /home/mla/.ssh/mla_key.pub >> /home/mla/.ssh/authorized_keys \
      && chown -R mla:mla /home/mla/.ssh \
      && sed -i '58s/no/yes/' /etc/ssh/sshd_config \
      && systemctl restart sshd"
  end
end
