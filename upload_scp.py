import re
import sys
import os
import subprocess
import shlex
from threading import Thread

class UploadScp(Thread):
    def __init__ (self,file,opts):
        Thread.__init__(self)
        self.file = file
        self.opts = opts
        self.status = -1
    def run(self):
        opts = self.opts.upload_scp_opts if self.opts.upload_scp_opts != None else ""
        self.scp_cmd = "scp %s %s %s" % (opts, self.file, self.opts.upload_scp)
        scp_retcode = subprocess.call(shlex.split(self.scp_cmd))
        self.status = scp_retcode