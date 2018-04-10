FROM ubuntu:latest
MAINTAINER ishidakazuya

# locale settings
ENV HOME=/root \
    DEBIAN=noninteractive \
    LANG=ja_JP.UTF-8 \
    LC_ALL=${LANG} \
    LANGUAGE=${LANG} \
    TZ=Asia/Tokyo \
    DISPLAY=:0
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# Install packages
RUN apt-get -y update && \
    apt-get -y install supervisor xvfb xfce4 x11vnc scrot vim xfce4-terminal language-pack-ja-base language-pack-ja ibus-anthy fonts-takao && \
    apt -y install python3 python3-pip && \
    pip3 install --upgrade pip && \
    apt-get -y clean && \
    rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

# Install SAGE2_Streamer
RUN mkdir /root/SAGE2_Streamer
ADD ./python /root/SAGE2_Streamer

# Rename user directories
RUN LANG=C xdg-user-dirs-update --force

# Start supervisord
EXPOSE 5900
ADD ./desktop.conf /etc/supervisor/conf.d/
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]

