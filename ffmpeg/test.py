import subprocess
import io

buf = io.BytesIO()
cmd = 'ffmpeg -f x11grab -i :1.0 -vcodec rawvideo -preset ultrafast -f mpegts pipe:1'
buf = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout

