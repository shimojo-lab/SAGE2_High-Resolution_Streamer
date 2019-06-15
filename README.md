# High-Resolution SAGE2 Streamer
SAGE2 has a screen sharing functionality from client application window to SAGE2 Tiled display. However, the screen sharing functionality resolution depends on client resolution, because the functionality is just a window image copy to SAGE2 from client.
So, we have been developed a new screen sharing functionality with free resolution mechanism on SAGE2. That is a Python scripts for streaming a high-resolution application window to a SAGE2 Tiled Display Wall.
(This scripts requires Linux as the operating system of the SAGE2 client)

## Installation
### Requirements
- [SAGE2](http://sage2.sagecommons.org) (ver.3 is needed)
- [Python3](https://www.python.org)
- [TurboVNC](https://github.com/TurboVNC/turbovnc)
- [FFmpeg](https://github.com/FFmpeg/FFmpeg)
- [libXrender](https://launchpad.net/ubuntu/+source/libxrender)
- [jq](https://stedolan.github.io/jq)

### How to setup
1. Clone this repository and move into the directory
2. Run `pip install -r requirements.txt`

## How to use
1. Launch the SAGE2 server.
2. Edit the configuration file (config.json).
3. Run `bash launch_vnc_server.sh`.
4. Run `python SAGE2_Streamer.py`.
