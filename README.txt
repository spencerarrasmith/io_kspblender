         A         
        / \       
       | 0 |       
       |___|       
       |___|       
       |KSP|       
      /|   |\     
     /| \_/ |\   
    /_|  W  |_\   
       @WWW@       
     @@WWWWW@@     
    @ @@@@ @@@ @   
  @   @  @@  @   @ 
 

KSPBLENDER .90
3/1/2015
SPENCER ARRASMITH
GITHUB.COM/DASOCCERGUY/KSPBLENDER
DASOCCERGUY39@GMAIL.COM

Thanks for checking out the readme!



INITAL SETUP

To get this working, you will need to change kspdir to the installation location of Kerbal Space Program

1. Find KSP.exe (look in Steam\Steamapps\common\Kerbal Space Program)
2. Copy the directory name
3. Paste it into kspdir.txt
4. In Blender, press CTRL+ALT+U, go to Addons, and enable this addon. It is called "Import-Export: KSPBlender .craft Import"
5. Either click "Save User Settings" or come back and enable the addon every time you want to use it.
6. Enjoy!



MOD PARTS

It's going to be hard for me to add support for every mod, but you can "easily" do it yourself!

1. Open "part_dir.py" and look at what it's doing.
2. Every part has a name that is mapped to the location of the model file.
3. Open up a .craft file with the mod parts you wish to use so you can see what the part is called (IT's NEVER THE SAME AS IN THE VAB OR SPH)
4. Create new entries for each mod part, following the form in the part_dir function. The last element ("engine","utility", etc) should be the name of the mod.