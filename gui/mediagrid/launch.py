#    launch.py is part of Mediagrid by Luca Franceschini & Luca Carrubba.
#    For info: www.gemq.info
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
	import struct
	import os
	import fnmatch
	import shutil
	import platform
	import subprocess
except:
	print "ERROR: You need struct, os, fnmatch, shutil, subprocess and platform Python Libraries"

try:
	import pyext
except:
	print "ERROR: This script must be loaded by the PD/Max pyext external"

#create a thumb .ppm from a file
def gen_thumb(filename, out_path, filemime, id_mg, start_mg, ffmpeg, self, myos, thumbsave):
    newthumb = "%s%s%d%s" % (id_mg, "-", start_mg, ".ppm")
    aud_pat=str(os.path.dirname(os.path.abspath(__file__))+"/default/audio.ppm")
    err_pat=str(os.path.dirname(os.path.abspath(__file__))+"/default/error.ppm")
    if filemime == 3:
        shutil.copy(aud_pat, os.path.join(out_path, newthumb))
    else:
        path_thumbsave = os.path.join(os.path.dirname(filename), ".mediagrid", "%s%s" % (os.path.splitext(os.path.basename(filename))[0], ".ppm"))
        if (thumbsave == 1) and (os.path.isfile(path_thumbsave)):
            shutil.copy(path_thumbsave, os.path.join(out_path, newthumb))
        else:
            if filemime == 1:
                middle = get_duration(filename, ffmpeg, myos)/2
                commandln = [ffmpeg, "-ss", humanize_time(middle), "-vframes", "1", "-i", filename, "-vcodec", "ppm", "-f", "image2", "-s", "60x40", os.path.join(out_path, newthumb)]
            if filemime == 2:
                commandln = [ffmpeg, "-i", filename, "-vcodec", "ppm", "-f", "image2", "-s", "60x40", os.path.join(out_path, newthumb)]
            try:
                startupinfo = None
                if myos == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                p = subprocess.Popen(commandln, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.wait()
                if (p.returncode == 1):
                    shutil.copy(err_pat, os.path.join(out_path, newthumb))
                    self._outlet(2,"Error on thumb creation")
                else:
                    if thumbsave == 1:
                        if not os.path.exists(os.path.join(os.path.dirname(filename), ".mediagrid")):
                            os.makedirs(os.path.join(os.path.dirname(filename), ".mediagrid"))
                        shutil.copy(os.path.join(out_path, newthumb), path_thumbsave)
            except:
                shutil.copy(err_pat, os.path.join(out_path, newthumb))
                self._outlet(2,"No FFmpeg installed?")
    return

#check the mime type of a file (1 video, 2 image, 3 audio, 0 no mime)
def file_type(filename):
    import mimetypes
    type = mimetypes.guess_type(filename)[0]
    if type is None:
        return 0
    type = type.split("/")[0]
    if type == "audio":
        return 3
    elif type == "image":
        return 2
    elif type == "video":
        return 1
    return 0

#check the duration of a video file
def get_duration(filename, ffmpeg, myos):
    totsec = 2
    try:
        commandln = [ffmpeg, "-i", filename]
        startupinfo = None
        if myos == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen(commandln, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        for line in p.stderr:
            if 'Duration' not in line: continue
            fields = line.split()
            duration = fields[1].replace(',', '').split(".")[0].split(":")
            totsec = int(duration[0])*3600 + int(duration[1])*60 + int(duration[2])
            break
    except:
        return totsec
    return totsec

#humanize time
def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)

#return the id of last created in mediagrid
def lastid(out_path, id_mg):
    if os.path.isfile(os.path.join(out_path, id_mg)):
      fin = open(os.path.join(out_path, id_mg), "rb")
      try:
        return struct.unpack('i', fin.read(4))[0]
      except:
        return 0
    return 0


class capture(pyext._class):

	# number of inlets and outlets
	_inlets=5
	_outlets=2

	# methods for all inlets
	outs = [] 

	tmp=0
	width=0
	height=0
	font=0
	max_mg=0
	
	firstarg = []
	
	in_path = []
	out_path = []
	id_mg = 0
	max_mg = 0
	
	
	# constructor
	def __init__(self,*args):
            self.firstarg = args[0]

	def _anything_1(self,*args):
            myos = platform.system()

            #do you want thumb saved in .mediagrid directory?
            thumbsave = 0

            ffmpeg = "ffmpeg"
            if myos == "Windows":
                ffmpeg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
            elif myos == "Darwin":
                ffmpeg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg")
      
            start_mg = lastid(self.out_path, str(self.id_mg))
            if start_mg >= self.max_mg:
                start_mg = 0

            f = open(os.path.join(self.out_path, str(self.id_mg)),'w')

            if str(args[0]) == "d":
                filecount = 0
                for fileorig in os.listdir(self.in_path):
                    filename = os.path.join(self.in_path, fileorig)
                    if os.path.isfile(filename):
                        filemime = file_type(filename)
                        if filemime > 0 and filecount < self.max_mg:
                            filecount = filecount + 1
                            start_mg = start_mg + 1
                            output = "%d%s%s" % (start_mg, " ", filename)
                            self._outlet(1, output)     
                            gen_thumb(filename, self.out_path, filemime, self.id_mg, start_mg, ffmpeg, self, myos, thumbsave)
                            f.seek(0)
                            f.write(struct.pack('i', start_mg))
                            f.truncate()
                        if start_mg == self.max_mg:
                            start_mg = 0
        
            if str(args[0]) == "f":
                if os.path.isfile(self.in_path):
                    filemime = file_type(self.in_path)
                    if filemime > 0:
                        start_mg = start_mg + 1
                        output = "%d%s%s" % (start_mg, " ", self.in_path)
                        self._outlet(1,output)
                        gen_thumb(self.in_path, self.out_path, filemime, self.id_mg, start_mg, ffmpeg, self, myos, thumbsave)
                        f.seek(0)
                        f.write(struct.pack('i', start_mg))
                        f.truncate()

            f.close()

	def _anything_2(self,*args):
            self.in_path = str(args[0])

	def _anything_3(self,*args):
            self.out_path = os.path.abspath(str(args[0]))

	def float_4(self, f):
            self.id_mg = int(f)

	def float_5(self, f):
            self.max_mg = int(f)
