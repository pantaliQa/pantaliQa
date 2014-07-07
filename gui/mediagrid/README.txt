DESCRIPTION

Mediagrid object is an abstraction let you pick a file from your disk in a graphical way. You can preload onto the mediagrid a video, image or audio file.

Mediagrid abstraction is inspired from Videogrid external from PDVJtools package by Sergi Lario and Lluis Gomez i Bigorda. The big difference is that mediagrid can manage also audio files and it works on all platforms.


Mediagrid was developped as part of gemQ project. more info: www.gemq.info

PREREQUISITES

1) Ffmpeg: you need to install ffmpeg binary for your os in order to work with mediagrid.
-linux: install ffmpeg in your system. If you are on a debian based system (like ubuntu) open a terminal and write 
sudo aptitude install ffmpeg
-Mac os X: install ffmpeg binary in mediagrid's directory
-windows: put your ffmpeg binary in mediagrid's directory

You can find ffmpeg binary for mac and windows in our repository:

svn checkout http://code.autistici.org/svn/planetQ/trunk/Mac/mediagrid/

2) py external for puredata from Thomas Grill.
Download pyext binary for your platform from Grill's website:

http://grrrr.org/ext/beta/

For how to install an external to your puredata installation refer to this page:

INSTALL

Copy mediagrid dir in your pd working directory or put mediagrid dir in your pd path.


THANKS
Thanks to all pd community specially to Hans Cristopher Steiner, Thomas Grill and other I don't know the name but they helped a lot by chat :) (dtmod?)
daje!
