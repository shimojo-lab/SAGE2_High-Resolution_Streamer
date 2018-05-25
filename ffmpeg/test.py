import ffmpeg

stream = ffmpeg.input(':1.0+0,0', f='x11grab', video_size=(1000, 1000))
stream = ffmpeg.output(stream, 'a.jpg',
                       f='image2', vcodec='mjpeg', vframes=1, qmin=1, qmax=100, q=1000)
print(ffmpeg.get_args(stream))
ffmpeg.run(stream)

