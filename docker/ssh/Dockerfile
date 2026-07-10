FROM ubuntu:22.04

RUN apt-get update && apt-get install -y openssh-server nano && \
    mkdir /var/run/sshd && \
    useradd -m -s /bin/bash user && \
    echo "user:password123" | chpasswd && \
    chmod u+s /usr/bin/nano && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    echo "root:toor" | chpasswd

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
