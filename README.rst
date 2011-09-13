================================================
html5video-helper - HTML5 Video encoding toolbox
================================================

This script is a little helper for encoding videos targeted for html5 use. If you have encoding parameter suggestions for better video quality please let me know.

**DISCLAIMER:** In the current state the script is a bit ugly as it was my first python script and it's some kind of hacked, anyhow it works perfectly for me. But I can't quarante that this script works for in all cases and that it doesn't damage everything.

Installation
------------
You need ffmpeg installed and usable via Terminal - it have to be in your PATH.

All you have to do then is to simply clone the repository and execute ./encode2all in a Terminal giving it the needed parameters.

Usage
-----
    Usage: encode2all.py -i INPUT_FILE -o OUTPUT_FOLDER ...

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit

      General Options:
        Some general options to configure the encoding processes

        -t THREADS, --threads=THREADS
                            Number of threads to encode with
        -q, --quiet         Don't show the output of ffmpeg and other tools

      File Options:
        All file related Options are done here.

        -i INPUT_FILE, --input=INPUT_FILE
                            movie file which should be converted
        -o OUTPUT_FOLDER, --output-folder=OUTPUT_FOLDER
                            folder where the encoded files should be stored
        -n OUTPUT_NAME, --output-name=OUTPUT_NAME
                            file name which the encoded videos should begin with.
                            Will be extended with resolution and format extension.

      Container Format Selection:
        Select which containers/formats you want to have the input movie
        encoded to. WebM, h264 and ogg/theora are enabled by default.

        --webm              Don't encode to WebM
        --ogg               Don't encode to ogg/theora
        --h264              Don't encode to h264

      Resolution Options:
        Select which format/resolution you want your movie encoded to. 1080p,
        720p and 360p are default if the movie has the resolution for it.

        --1080p             Don't encode at 1080p
        --720p              Don't encode at 720p
        --360p              Don't encode at 360p

      Output and Upload Options:
        Do you want to automatically upload the encoded files?

        --scp=UPLOAD_SCP    Upload via scp. Example value: user@host:/directory/
        --scp-opts=UPLOAD_SCP_OPTS
                            Additional SCP options like "-i foo/blub" for aspecific identity file.
                            At the moment you have to start an ssh-agent with an opened key if you want to use this.