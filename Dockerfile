FROM centos:latest
MAINTAINER ishidakazuya

# Install packages
RUN yum -y update \
&& yum -y install epel-release \
&& yum -y groupinstall 'Mate Desktop' \
&& yum -y install https://centos7.iuscommunity.org/ius-release.rpm \
&& yum -y install python36u python36u-libs python36u-devel python36u-pip supervisor \
&& yum -y install http://downloads.sourceforge.net/project/virtualgl/2.5.2/VirtualGL-2.5.2.x86_64.rpm \
&& yum -y install http://downloads.sourceforge.net/project/turbovnc/2.1.2/turbovnc-2.1.2.x86_64.rpm \
&& yum -y clean all \
&& pip3.6 install --upgrade pip \
&& echo "exec vglrun mate-session &" > /root/.Xclients \
&& chmod 777 /root/.Xclients

# Set ENVs
LABEL com.nvidia.volumes.needed="nvidia_driver"
ENV DISPLAY=:0 \
    PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH} \
    LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64 \
    QT_X11_NO_MITSHM=1

# Install SAGE2_Streamer
RUN mkdir /root/SAGE2_Streamer
ADD ./python /root/SAGE2_Streamer

# Start supervisord
EXPOSE 5901
ADD ./vncserver.conf /etc/supervisor/conf.d/
CMD /usr/bin/supervisord -c /etc/supervisor/supervisord.conf

