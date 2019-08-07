# AnimatedFits
Scripts for making pedagogical animations illustrating fundamental concepts for fitting functions to distributions to extract model parameters.

## How to run
Run like this:

```
python3 animated-fits.py
```

In the beginning of the code there are switches for controlling the functional form of the true distribution (gaussian, square pulse, 2nd degree polynomial for now) and whether to run in batch or interactive mode. The script dumps out a series of frames as pngs and pdfs, and these can be combined into animations through the `encode.sh` script (relying on `ffmpeg`).  
