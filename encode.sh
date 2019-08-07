# make movie with animation
ffmpeg -framerate 5 -start_number 000 -i fit_Gauss_%04d.png -vcodec libx264 fit_Gauss.mp4
