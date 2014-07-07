#    utils.py is part of Mediagrid by Luca Franceschini & Luca Carrubba.
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
    import os
    import glob
    import commands
    import sys
    import shutil
    from subprocess import Popen,PIPE
    import platform
    import re
except:
    print "ERROR: You need os, subprocess, platform Python Libraries"

try:
    import pyext
except:
    print "ERROR: This script must be loaded by the PD/Max pyext external"

#class that format the textfile
class formattext(pyext._class):
    
    # number of inlets and outlets
    _inlets=2
    _outlets=1

    # methods for all inlets
    outs = []
	
    firstarg = []

    in_text = []
    id_text = 0

    # constructor
    def __init__(self,*args):
        print "formattext object loaded"

    def _anything_1(self,*args):
        self.in_text = os.path.abspath(str(args[0]))
		
	try:
	    f = open(self.in_text, "r")
            try:
		allfile = f.read()
	    finally:
		f.close()
	except IOError:
	    pass

	plat={"Windows":"\r\n", 'Linux':"\n", 'Darwin':"\n"}
	myos = platform.system()
	out_path = "/tmp/"
	
	fullwords = re.findall(r'\w+', allfile)
	newname = "%s%s%d%s" % ("textplayer", "-", self.id_text, ".txt") 
	newfile = open(os.path.join(out_path, newname), 'w')

	for i in fullwords:
	    newfile.write( i + plat[myos] )
        
        self._outlet(1, os.path.join(out_path, newname))

    def int_2(self, f):
	self.id_text = int(f)

#class that load fonts
class loadfonts(pyext._class):

    # number of inlets and outlets
    _inlets=1
    _outlets=1

    # methods for all inlets
    outs = []
	
    firstarg = []
	
    font_path = []
    cont=0

    # constructor
    def __init__(self,*args):
        print "loadfonts object loaded"

    def _anything_1(self,*args):
        self.font_path = os.path.abspath(str(args[0]))
        self.cont=0	
        out_path = os.path.join(self.font_path, "fonts")
        plat={"Windows":"C:\WINDOWS\Fonts", "Linux":"/usr/share/fonts", "Darwin":"/Library/Fonts" }
        myos = platform.system()           
        in_path = os.path.abspath(plat[myos])

        #on windows we use the default fonts dir
        if myos == "Windows":
            for root, dirs, files in os.walk(in_path):
 	        files = [ fi for fi in files if fi.endswith(".ttf") | fi.endswith(".otf") ]
 	        for i in files:
 	            self.cont +=1
 	            self._outlet(1, self.cont, i)
        #on posix platform we create symbolic links
        else:
            if not os.path.exists(out_path):
                os.makedirs(out_path)
        
                #list all chars and create symb links
                for root, dirs, files in os.walk(in_path):
                    if myos == "Darwin":
                        files = [ fi for fi in files ]
                    if myos == "Linux":
                        files = [ fi for fi in files if fi.endswith(".ttf") ]
                    for i in files:
                        char = os.path.join(root,i)
                        charlink = os.path.join(out_path, i)
                        self.cont +=1
                        if not os.path.exists(charlink):
                            os.symlink(char, charlink)
                            self.cont +=1
                            self._outlet(1,self.cont, i)

            #font dir exist then only list
            else:
                for root, dirs, files in os.walk(out_path):
                    if myos == "Darwin":
                        files = [ fi for fi in files ]
                    if myos == "Linux":
                        files = [ fi for fi in files if fi.endswith(".ttf") ]
                    for i in files:
                        self.cont +=1
                        self._outlet(1, self.cont, i)
                        
#class that detect cam devices
class loadcams(pyext._class):

	# number of inlets and outlets
	_inlets=1
	_outlets=1

	# methods for all inlets
	outs = []
	
	firstarg = []
	
	# constructor
	def __init__(self,*args):
            print "loadcams object loaded"

	def bang_1(self):
            myos = platform.system()
            
            #linux system
            if myos == "Linux":
                webcam = []
                com = "v4l-info "
                for element in glob.glob('/dev/video*'):
                    webcam.append(element)
                    webcam.reverse()
                for web in webcam:
                    name = commands.getoutput(com+web+' |grep card')
                    a,b = name.split('card')
                    cam = b.split(':')[1]
                    output = cam.split('"')[1]
                    self._outlet(1, output)

class screeninfo(pyext._class):
    # number of inlets and outlets
    _inlets=1
    _outlets=2

    # methods for all inlets    
    outs = []
    
    firstarg = []
    
    # constructor
    def __init__(self,*args):
        print "screeninfo object loaded"

    def bang_1(self):
     myos = platform.system()

        #on Mac
     if myos == "Darwin":
         try:
              	import AppKit
         except:
                print"You need pyObjc module installed"
                print "In 10.5 or highter it is supposed to be installed by default on your system"
                print "If Your system is 10.4 you need to install the package module pyobjc"
         sc=[(screen.frame().size.width, screen.frame().size.height) for screen in AppKit.NSScreen.screens()]
         xa,ya= sc[0]

         if len(sc) == 1: 
            print "no secondary monitor"
            self._outlet(1, int(xa),int(ya), 0, 0 )
            self._outlet(2,0)
         else:
             xb,yb= sc[1]
             self._outlet(1,int(xa),int(ya), int(xb),int(yb))
             self._outlet(2,1)

        #on linux 
     elif myos == "Linux":
         try:
             import wx
         except:
             print "You must install wxpython-2.6"
                
         app = wx.App(0)
      	 count=wx.Display().GetCount()
         #check the graphic card vendor 
	 dic = get_graphic_card_vendor()
         if str(dic)== "nVidia Corporation": 
		 if int(count) == 1: 
		     print "no secondary monitor"
	       	     sc=wx.Display(0).GetGeometry()
		     xa= sc[2]
		     ya= sc[3]
		     self._outlet(1, int(xa),int(ya), 0, 0 )
		     self._outlet(2,0)
		 else:
		     sc=wx.Display(1).GetGeometry()
		     xa= sc[0]
		     ya= sc[1]
		     xb= sc[2]
		     yb= sc[3]
		     self._outlet(1,int(xa),int(ya), int(xb),int(yb))
		     self._outlet(2,1)
	 else:
		#es una intel (or ATI)
		 if int(count) == 1: 
		     print "no secondary monitor"
	       	     sc=wx.Display(0).GetGeometry()
		     xa= sc[2]
		     ya= sc[3]
		     self._outlet(1, int(xa),int(ya), 0, 0 )
		     self._outlet(2,0)
		 else:
		     sc=wx.Display(0).GetGeometry()
		     xa= sc[0]
		     ya= sc[1]
		     xb= sc[2]
		     yb= sc[3]
		     self._outlet(1,int(xa),int(ya), int(xb),int(yb))
		     self._outlet(2,1)
				
     else:
         try:
             import wx
         except:
             print "You must install wxpython-2.6"
                
         app = wx.App(0)
      	 count=wx.Display().GetCount()

         if int(count) == 1: 
             print "no secondary monitor"
       	     sc=wx.Display(0).GetGeometry()
             xa= sc[2]
             ya= sc[3]
             self._outlet(1, int(xa),int(ya), 0, 0 )
             self._outlet(2,0)
         else:
             sc=wx.Display(1).GetGeometry()
             xa= sc[0]
             ya= sc[1]
             xb= sc[2]
             yb= sc[3]
             self._outlet(1,int(xa),int(ya), int(xb),int(yb))
             self._outlet(2,1)	  
	     




#class that format the textfile
class converter(pyext._class):
    
    # number of inlets and outlets
    _inlets=4
    _outlets=2

    # methods for all inlets
    outs = []
	
    firstarg = []

    in_path = 0
    out_path = 0
    ratio = 0
    tot_dir = 0
    tot_video = 0

    # constructor
    def __init__(self,*args):
        print "QVideoConverter object loaded"
    def bang_1(self):
	 checksys = platform.system()
	 ratio=self.ratio
	 ffmpeg = "ffmpeg"
    	 if checksys == "Windows":
        	ffmpeg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../patches/gui/mediagrid/ffmpeg.exe")
    	 elif checksys == "Darwin":
        	ffmpeg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../patches/gui/mediagrid/ffmpeg")
    	 for root, subFolders, files in os.walk(self.in_path):
		for file in files:
	            filename = os.path.join(root,file)
	            if file_type(filename):
	                convertfile(filename, self.in_path, self.out_path, ratio, ffmpeg)
	                self.tot_video = self.tot_video + 1
    	 print ""
    	 print "%d dir created and %d videos converted." % (self.tot_dir,self.tot_video)
	 self._outlet(1, self.tot_video)
	 self._outlet(2, "bang")

    
    def _anything_2(self,*args):
        self.in_path = os.path.abspath(str(args[0]))
	if not os.path.isdir(self.in_path):
                print "Input directory is not valid"
                print "You must insert a valid directory"
	for root, subFolders, files in os.walk(self.in_path):
        	for cartella in subFolders:
            		self.rel_path = os.path.join(self.out_path,os.path.relpath(os.path.join(root,cartella),self.in_path))
            		if not os.path.isdir(self.rel_path):
                		os.mkdir(self.rel_path)
             			print 'dir create: %s' % self.rel_path
              			self.tot_dir = self.tot_dir + 1

    def _anything_3(self, *args):
	self.out_path = os.path.abspath(str(args[0]))
	if not os.path.isdir(self.out_path):
                print "Input directory is not valid"
                print "You must insert a valid directory"
	if not os.path.isdir(self.out_path):
        	os.mkdir(self.out_path)
        	print 'dir create: %s' % self.out_path
		self.tot_dir = self.tot_dir + 1

    def _anything_4(self, *args):
	self.ratio=str(args[0])





#this function return 1 if is a video file
def file_type(filename):
    import mimetypes
    type = mimetypes.guess_type(filename)[0]
    if type is None:
        return 0
    type = type.split("/")[0]
    if type == "video":
        return 1
    return 0

#convert the file
def convertfile(filename, in_path, out_path, ratio, ffmpeg):
    newfile = "%s%s" % (os.path.splitext(os.path.relpath(filename,in_path))[0], ".mov")
    newfile2 = os.path.join(out_path, newfile)
    print '%s -> %s' % (filename, newfile2)
    if ratio:
        try:
            p = Popen([ffmpeg, "-i", filename, "-an", "-sameq", "-vcodec", "mjpeg", "-f", "mov", "-y", "-s", ratio, newfile2], stdout=PIPE, stderr=PIPE)
	    p.wait()
            if (p.returncode == 1):
                print "Error on FFMPEG thumb creation"
        except:
            print "No FFMPEG library?"
    else:
        try:
            p = Popen([ffmpeg, "-i", filename, "-an", "-sameq", "-vcodec", "mjpeg", "-f", "mov", "-y", newfile2], stdout=PIPE, stderr=PIPE)
            p.wait()
	    
            if (p.returncode == 1):
                print "Error on FFMPEG thumb creation"
        except:
            print "No FFMPEG library?"
    return

#get pci vendor infos of the graphic card on linux
def get_graphic_card_vendor():
    import dbus
    bus = dbus.SystemBus()
    hal_manager_object = bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
    prop = 'pci.device_class'
    for device in hal_manager_object.get_dbus_method('GetAllDevices', 'org.freedesktop.Hal.Manager')():
        dev = bus.get_object('org.freedesktop.Hal', device)
        interface = dbus.Interface(dev, dbus_interface='org.freedesktop.Hal.Device')
        if interface.PropertyExists(prop):
            if interface.GetProperty(prop) == 3:
                # we return the properties of the first device in the list
                # with a pci.device_class == 3 (should check if several such devs...
                dic=interface.GetAllProperties()
		for key, value in dic.iteritems():
    			if key=="pci.vendor":
				return(value)

