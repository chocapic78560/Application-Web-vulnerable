FROM ubuntu:22.04

# On met tout dans le même bloc pour forcer Docker à tout installer et appliquer le SUID d'un coup
RUN apt-get update && apt-get install -y openssh-server sudo nano && \
    mkdir /var/run/sshd && \
    # VULN: weak SSH credentials (misconfiguration)
    useradd -m -s /bin/bash user && \
    echo "user:password123" | chpasswd && \
    usermod -aG sudo user && \
    # VULN: root login permitted
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    echo "root:toor" | chpasswd && \
    # VULN: SUID misconfiguration sur nano (il est bien dans /usr/bin/nano après install)
    chown root:root /usr/bin/nano && \
    chmod u+s /usr/bin/nano

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
