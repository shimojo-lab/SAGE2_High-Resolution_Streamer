FROM ubuntu:latest

# locale settings
ENV HOME=/root \
    DEBIAN=noninteractive \
    LANG=ja_JP.UTF-8 \
    LC_ALL=${LANG} \
    LANGUAGE=${LANG} \
    TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# Install packages
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install supervisor xvfb xfce4 x11vnc scrot && \
    apt-get -y install git net-tools vim xfce4-terminal && \
    apt-get -y install language-pack-ja-base language-pack-ja ibus-anthy fonts-takao && \
    apt -y install python3 python3-pip
RUN pip3 install --upgrade pip3 && \
    pip3 install numpy tornado Xlib pyautogui && \
    apt-get -y clean && \
    rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

# Install SAGE2_Streamer
RUN cd /root && \
    git clone https://gitlab.ais.cmc.osaka-u.ac.jp/ishida/SAGE2_Streamer.git

# Rename user directories
RUN LANG=C xdg-user-dirs-update --force

# Start supervisord
EXPOSE 5900
ADD ./desktop.conf /etc/supervisor/conf.d/
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]

