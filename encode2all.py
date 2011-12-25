#!/usr/bin/python

from optparse import OptionParser,OptionGroup

import re
import sys
import os
import subprocess
import shlex
import hashlib
import time
from threading import Thread

from upload_scp import UploadScp


options = None
args = None
input_resolution = None
abs_input_file = None
outfile_name_base = None
thread_list = []



def prepare():
    global options, arg, input_resolution, abs_input_file, outfile_name_base

    abs_input_file = os.path.abspath(options.input_file)
    os.chdir(options.output_folder)

    ffmpeg_cmd = "ffmpeg -i %s" % (abs_input_file)
    ffmpeg = subprocess.Popen(shlex.split(ffmpeg_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in ffmpeg.stderr:
        if ": Video:" in line:
            line = re.sub("^.+Video", "", line)
            resol_re = re.compile('([0-9]{3,})x([0-9]{3,})')
            resol_match = re.search(resol_re, line)
            input_resolution = [int(resol_match.group(1)), int(resol_match.group(2))]
            outfile_name_base = re.sub(r'(\.[a-z0-9]+)$', r'', os.path.basename(abs_input_file))
            if (options.output_name == None):
              outfile_name_base = re.sub(r'(\.[a-z0-9]+)$', r'', os.path.basename(abs_input_file))
            else:
              outfile_name_base = options.output_name


def enc1080p():
    global options, abs_input_file, input_resolution, outfile_name_base

    if options.r1080p:
        if (input_resolution[0] >= 1920) and (input_resolution[1] >= 1080) and (input_resolution[0]/input_resolution[1] == 16/9):
            # webm
            ffmpeg_video_param = "-b 5632k"
            ffmpeg_audio_param = "-ab 192k"
            enc_webm(ffmpeg_video_param, ffmpeg_audio_param, [1920, 1080])

            # theora
            ffmpeg_video_param = "-vb 6144k"
            ffmpeg_audio_param = "-ab 192k"
            enc_theora(ffmpeg_video_param, ffmpeg_audio_param, [1920, 1080])

            # h264
            ffmpeg_video_param = "-b 5632k"
            ffmpeg_audio_param = "-ab 192k"
            enc_h264(ffmpeg_video_param, ffmpeg_audio_param, [1920, 1080])


def enc720p():
    global options, abs_input_file, input_resolution, outfile_name_base

    if options.r720p:
        if (input_resolution[0] >= 1280) and (input_resolution[1] >= 720) and (input_resolution[0]/input_resolution[1] == 16/9):
            # webm
            ffmpeg_video_param = "-b 2816k"
            ffmpeg_audio_param = "-ab 160k"
            enc_webm(ffmpeg_video_param, ffmpeg_audio_param, [1280, 720])

            # theora
            ffmpeg_video_param = "-vb 3328k"
            ffmpeg_audio_param = "-ab 160k"
            enc_theora(ffmpeg_video_param, ffmpeg_audio_param, [1280, 720])

            # h264
            ffmpeg_video_param = "-vb 2816k"
            ffmpeg_audio_param = "-ab 160k"
            enc_h264(ffmpeg_video_param, ffmpeg_audio_param, [1280, 720])


def enc360p():
    global options, abs_input_file, input_resolution, outfile_name_base

    if options.r360p:
        if (input_resolution[0] >= 640) and (input_resolution[1] >= 360) and (input_resolution[0]/input_resolution[1] == 16/9):
            # webm
            ffmpeg_video_param = "-b 1024k"
            ffmpeg_audio_param = "-ab 128k"
            enc_webm(ffmpeg_video_param, ffmpeg_audio_param, [640, 360])

            # theora
            ffmpeg_video_param = "-vb 1280k"
            ffmpeg_audio_param = "-ab 128k"
            enc_theora(ffmpeg_video_param, ffmpeg_audio_param, [640, 360])

            # h264
            ffmpeg_video_param = "-vb 1024k"
            ffmpeg_audio_param = "-ab 128k"
            enc_h264(ffmpeg_video_param, ffmpeg_audio_param, [640, 360])


def enc_webm(video_params, audio_params, resolution):
    global options, abs_input_file, input_resolution, outfile_name_base

    if options.webm:
        logfile = "%s_%d.webmlog" % (outfile_name_base, resolution[1])
        outfile = "%s_%d.webm" % (outfile_name_base, resolution[1])
        ffmpeg_pre = "ffmpeg -pass %d -passlogfile " + logfile
        ffmpeg_pre += " -i %s -f webm -vcodec libvpx -threads %d -s %dx%d -aspect 16:9 -keyint_min 0 -g 75 -skip_threshold 0 -qmin 10 -qmax 51 " % (abs_input_file, options.threads, resolution[0], resolution[1])
        ffmpeg_pre += video_params
        ffmpeg_audio = "-acodec libvorbis -ar 44100 -ac 2 -vol 300 %s" % (audio_params)
        ffmpeg_pass1_cmd = ffmpeg_pre % (1)
        ffmpeg_pass1_cmd += " -an -y /dev/null"
        ffmpeg_pass2_cmd = ffmpeg_pre % (2)
        ffmpeg_pass2_cmd += " %s %s" % (ffmpeg_audio, outfile)
        exec_cmd(ffmpeg_pass1_cmd)
        exec_cmd(ffmpeg_pass2_cmd)
        cleanup_passlog(logfile)
        upload(outfile)

def enc_theora(video_params, audio_params, resolution):
    global options, abs_input_file, input_resolution, outfile_name_base

    if options.ogg:
        outfile = "%s_%d.ogv" % (outfile_name_base, resolution[1])
        ffmpeg_cmd = "ffmpeg -i %s -f ogg -vcodec libtheora -threads %d -s %dx%d -aspect 16:9 " % (abs_input_file, options.threads, resolution[0], resolution[1])
        ffmpeg_cmd += video_params
        ffmpeg_cmd += " -acodec libvorbis -ar 44100 -ac 2 -vol 300 %s %s" % (audio_params, outfile)
        exec_cmd(ffmpeg_cmd)
        upload(outfile)

def enc_h264(video_params, audio_params, resolution):
    global options, abs_input_file, input_resolution, outfile_name_base

    if options.h264:
        outfile = "%s_%d.mp4" % (outfile_name_base, resolution[1])
        ffmpeg_pre = "ffmpeg -pass %d"
        ffmpeg_pre += " -i %s -f mp4 -vcodec libx264 -threads %d -s %dx%d -aspect 16:9 -g 75 -coder 0 -bf 0 -flags2 'wpred-dct8x8' -wpredp 0 " % (abs_input_file, options.threads, resolution[0], resolution[1])
        ffmpeg_pre += video_params
        ffmpeg_audio = "-strict experimental -acodec aac -ar 44100 -ac 2 -vol 300 %s" % (audio_params)
        ffmpeg_pass1_cmd = ffmpeg_pre % (1)
        ffmpeg_pass1_cmd += " -an -y /dev/null"
        ffmpeg_pass2_cmd = ffmpeg_pre % (2)
        ffmpeg_pass2_cmd += " %s %s" % (ffmpeg_audio, outfile)
        exec_cmd(ffmpeg_pass1_cmd)
        exec_cmd(ffmpeg_pass2_cmd)
        cleanup_h264_passlog()
        upload(outfile)


def cleanup_passlog(wished_name):
    if os.path.isfile(wished_name):
        os.unlink(wished_name)
    elif os.path.isfile("passlogfile-0.log"):
        os.unlink("passlogfile-0.log")

def cleanup_h264_passlog():
    if os.path.isfile("x264_2pass.log"):
        os.unlink("x264_2pass.log")
    if os.path.isfile("x264_2pass.log.temp"):
        os.unlink("x264_2pass.log.temp")
    if os.path.isfile("x264_2pass.log.mbtree"):
        os.unlink("x264_2pass.log.mbtree")


def upload(file):
    global options, thread_list

    if options.upload_scp != None:
        uploader = UploadScp(file, options)
        thread_list.append(uploader)
        uploader.start()

def exec_cmd(cmd):
    out=subprocess.PIPE
    if options.verbose:
        print "Executing:"
        print cmd + "\n"
        out=None
    process = subprocess.Popen(shlex.split(cmd), stdout=out, stderr=out)
    if process.wait() != 0:
        print "Something went wrong."
        if not options.verbose:
            print "You may use verbose (non-quiet mode)."


def get_temp_file_name(hashbase):
    hashbase = str(hashbase)
    hashbase += time.asctime(time.gmtime())
    return hashlib.sha1(hashbase).hexdigest()


def parse_args():
    global options, args

    parser = OptionParser(usage="%prog -i INPUT_FILE -o OUTPUT_FOLDER ...", version="%prog 0.1")

    # general group
    general_group = OptionGroup(parser, "General Options", "Some general options to configure the encoding processes")
    general_group.add_option("-t", "--threads", dest="threads", default=0, type="int", help="Number of threads to encode with")
    general_group.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="Don't show the output of ffmpeg and other tools")
    parser.add_option_group(general_group)

    # file group
    file_group = OptionGroup(parser, "File Options", "All file related Options are done here.")
    file_group.add_option("-i", "--input", dest="input_file", help="movie file which should be converted")
    file_group.add_option("-o", "--output-folder", dest="output_folder", help="folder where the encoded files should be stored")
    file_group.add_option("-n", "--output-name", dest="output_name", help="file name which the encoded videos should begin with. Will be extended with resolution and format extension.")
    parser.add_option_group(file_group)

    # container group
    container_group = OptionGroup(parser, "Container Format Selection", "Select which containers/formats you want to have the input movie encoded to. WebM, h264 and ogg/theora are enabled by default.")
    container_group.add_option("--webm", action="store_false", dest="webm", default=True, help="Don't encode to WebM")
    container_group.add_option("--ogg", action="store_false", dest="ogg", default=True, help="Don't encode to ogg/theora")
    container_group.add_option("--h264", action="store_false", dest="h264", default=True, help="Don't encode to h264")
    parser.add_option_group(container_group)

    # resolution group
    resolution_group = OptionGroup(parser, "Resolution Options", "Select which format/resolution you want your movie encoded to. 1080p, 720p and 360p are default if the movie has the resolution for it.")
    resolution_group.add_option("--1080p", action="store_false", dest="r1080p", default=True, help="Don't encode at 1080p")
    resolution_group.add_option("--720p", action="store_false", dest="r720p", default=True, help="Don't encode at 720p")
    resolution_group.add_option("--360p", action="store_false", dest="r360p", default=True, help="Don't encode at 360p")
    parser.add_option_group(resolution_group)
    
    # upload group
    upload_group = OptionGroup(parser, "Output and Upload Options", "Do you want to automatically upload")
    upload_group.add_option("--scp", dest="upload_scp", default=True, help="Upload via scp. Example value: user@host:/directory/")
    upload_group.add_option("--scp-opts", dest="upload_scp_opts", default=True, help="Additional SCP options like \"-i foo/blub\" for a specific identity file.\nAt the moment you have to start an ssh-agent with an opened key if you want to use this.")
    parser.add_option_group(upload_group)

    (options, args) = parser.parse_args()

    if (options.output_folder == None) or (options.input_file == None):
        print >> sys.stderr, "Error: You have to give an input file and an output folder!\n"
        parser.print_help()
        exit(1)

def main():
    global thread_list
    print "Starting encode2all.py at '%s'\n\n" % (time.ctime())

    parse_args()
    prepare()
    enc360p()
    enc720p()
    enc1080p()
    
    # Wait for all threads to finish
    for t in thread_list:
        t.join()
        if t.status != 0:
            print "Upload '%s' failed with error code %d!" % (t.scp_cmd, t.status)
    
    print "\n\nEnding encode2all.py at '%s'" % (time.ctime())

if __name__ == "__main__":
    main()
