# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import mathutils

def zup_tuple(line):
    """changes from Unity Y-up world to Blender Z-up world"""
    zup = [float(i) for i in line.split(" ")[-1].split(",")]
    zup[1], zup[2] = zup[2], zup[1]
    return tuple(zup)

def zup_eul(line):
    """changes from Unity Y-up Left-Handed Quaternion to Blender Z-up Right-Handed Euler"""
    zup = [float(i) for i in line.split(" ")[-1].split(",")]
    zup = mathutils.Quaternion([0-zup[3], zup[0], zup[2], zup[1]])
    return (mathutils.Quaternion.to_euler(zup).x, mathutils.Quaternion.to_euler(zup).y, mathutils.Quaternion.to_euler(zup).z)

def zup_quat(line):
    """changes from Unity Y-up Left-Handed Quaternion to Blender Z-up Right-Handed Quaternion"""
    zup = [float(i) for i in line.split(" ")[-1].split(",")]
    zup = mathutils.Quaternion([0-zup[3], zup[0], zup[2], zup[1]])
    return zup


class kspcraft:
    """A Kerbal Space Program craft lol"""
    def __init__(self,filename):
        self.filename = filename
        self.lines = []
        self.ship = "0"
        self.version = "0"
        self.description = "0"
        self.type = "0"
        #self.size = None
        self.partslist = []
        self.partdatalist = []

        self.parse_file()
        self.set_data(self.lines[0:5])
        self.set_partslist(self.lines)

    def num_parts(self):
        """method to count the number of parts in the ship, as a sanity check"""
        try:
            return len(self.partslist)
        except TypeError:
            return 0
    
    def parse_file(self):
        """read in the plaintext .craft file"""
        fileobj = open(self.filename,'r',encoding='utf-8')
        text = fileobj.read()
        fileobj.close()
        self.lines = text.splitlines()

    def set_data(self,lines):
        """read over the first 5 lines to set ship data"""
        self.ship = " ".join(lines[0].split(" ")[2:])
        self.version = lines[1].split(" ")[2]
        self.description = " ".join(lines[2].split(" ")[2:])
        self.type = lines[3].split(" ")[2]
        #self.size = zup_tuple(lines[4])

    def set_partslist(self,lines):
        """find parts data by looking between each unindented { and the following \tEVENTS (\t is indentation)"""
        startindices = []
        endindices = []
        partdata = []
        for i in range(len(self.lines)):
            partdata.append(["None"])
            if self.lines[i]=="{":
                startindices.append(i)
            if self.lines[i]=="}":
                endindices.append(i)
               
        for i in range(len(startindices)):
            self.partslist.append(part(self.lines[startindices[i]:endindices[i]]))



class part:
    """A part for a ship lol"""
    def __init__(self,lines):
        self.lines = lines
        self.part = ""
        self.partNumber = 0
        self.partName = "0"
        self.partClass = "0"
        self.pos = (0,0,0)
        self.attPos = (0,0,0)
        self.attPos0 = (0,0,0)
        self.rot = (0,0,0)
        self.attRot = (0,0,0,0)
        self.attRot0 = (0,0,0,0)
        self.rotQ = (0,0,0,0)
        self.mir = (0,0,0)
        self.symMethod = "0"
        self.istg = 0
        self.dstg = 0
        self.sidx = 0
        self.sqor = 0
        self.sepI = 0
        self.attm = 0
        self.modCost = 0
        self.modMass = 0
        self.modSize = (0,0,0)
        self.tgt = 0
        self.tgtpos = (0,0,0)
        self.tgtrot = (0,0,0,0)
        self.tgtdir = (0,0,0)
        self.linklist = []
        self.attNlist = []
        self.symlist = []
        self.srfNlist = []
        self.xsections = []

        self.set_data(self.lines)

    def set_data(self,lines):
        """set part data based on first word of each line"""
        for line in lines:
            if line.split()[0] == "part":
                self.part = line.split(" ")[2]                                  #"part = Mark1-2Pod_4293084140" -> "Mark1-2Pod_4293084140" for object name
                self.partNumber = int(line.split("_")[1])                       #"part = Mark1-2Pod_4293084140" -> 4293084140 higher = higher in hierarchy (and to distinguish objects)
                self.partName = "".join(line.split("_")[0:-1]).split()[-1]      #"part = Mark1-2Pod_4293084140" -> "Mark1-2Pod" for mesh name
            #if line.split()[0] == "partName":
                #self.partName = " ".join(line.split()[2:])                     #"partName = Part" -> seems to always be Part, so kinda useless
            if line.split()[0] == "pos" and self.pos == (0,0,0):
                self.pos = zup_tuple(line)                                      #"pos = 0.003080267,7.645381,0.02017996" -> (0.003080267, 0.02017996, 7.645381)
            if line.split()[0] == "attPos":
                self.attPos = zup_tuple(line)                                   #"attPos = 0,0,0" -> (0,0,0) y<>z, attachment position? always seems to be (0,0,0)
            if line.split()[0] == "attPos0":
                self.attPos0 = zup_tuple(line)                                  #"attPos0 = 0,0,0" -> (0,0,0) y<>z, seems to always be (0,0,0) also
            if line.split()[0] == "rot" and self.rot == (0,0,0):
                self.rot = zup_eul(line)                                        #"rot = 0,0,0,1" -> (0,0,0) y<>z, made right-handed, converted to Euler angles
                self.rotQ = zup_quat(line)                                      #"rot = 0,0,0,1" -> (-1,0,0,0) w to beginning, y<>z, made right-handed
            if line.split()[0] == "attRot":
                self.attRot = zup_quat(line)                                    #"attRot = 0,0,0,1" -> (-1,0,0,0) w to beginning, y<>z, made right-handed
            if line.split()[0] == "attRot0":
                self.attRot0 = zup_quat(line)                                   #"attRot0 = 0,0,0,1" -> (-1,0,0,0) w to beginning, y<>z, made right-handed
            if line.split()[0] == "mir":
                self.mir = zup_tuple(line)                                      #"mir = 1,1,1" -> (1,1,1) not really sure what this is for
            if line.split()[0] == "symMethod":
                self.symMethod = line.split(" ")[2]                             #"symMethod = Radial" -> "Radial" would be different in SPH
            if line.split()[0] == "istg":
                self.istg = int(line.split()[2])                                #"istg = 0" -> 0 _______________?
            if line.split()[0] == "dstg":
                self.dstg = int(line.split()[2])                                #"dstg = 0" -> 0 ________________?
            if line.split()[0] == "sidx":
                self.sidx = int(line.split()[2])                                #"sidx = -1" -> -1 ______________?
            if line.split()[0] == "sqor":
                self.sqor = int(line.split()[2])                                #"sqor = -1" -> -1 _____________?
            if line.split()[0] == "sepI":
                self.sepI = int(line.split()[2])
            if line.split()[0] == "attm":
                self.attm = int(line.split()[2])                                #"attm = 0" -> 0 boolean for "is attachment?" thing that can be attached onto surface rather than connection node
            if line.split()[0] == "modCost":
                self.modCost = float(line.split()[2])                           #"modCost = 0" -> 0 ____________? (always 0)
            if line.split()[0] == "modMass":
                self.modMass = float(line.split()[2])                           #"modMass = 0" -> _______________? (always 0)
            if line.split()[0] == "modSize":                                    #(line below this one) "modSize = (0.0, 0.0, 0.0)" -> (0.0, 0.0, 0.0), y<>z
                self.modSize = tuple([float(" ".join(line.split()[2:]).split(", ")[0][1:]), float(" ".join(line.split()[2:]).split(", ")[2][0:-1]), float(" ".join(line.split()[2:]).split(", ")[1])])
            if line.split()[0] == "link":
                self.linklist.append(link(line))                                #new entry in list of links with new link instance
            if line.split()[0] == "attN":
                self.attNlist.append(attN(line))                                #new entry in list of attachments with new attN instance
            if line.split()[0] == "sym":
                self.symlist.append(sym(line))                                  #new entry in symmetrical parts list with new sym instance
            if line.split()[0] == "srfN":
                self.srfNlist.append(srfN(line))                                #"srfN = srfAttach,RCSTank1-2_4293083910" -> new entry in surface-attached-to list with new srfN instance
            if line.split()[0] == "cData":
                self.tgt = line.split()[3][0:-1]
                self.tgtpos = zup_tuple(line.split()[5][0:-1])
                self.tgtdir = zup_tuple(line.split()[7][0:-1])
            if line.split()[0] == "tgt":
                self.tgt = line.split()[-1]
            if line.split()[0] == "pos" and self.pos != (0,0,0):
                self.tgtpos = zup_tuple(line)
            if line.split()[0] == "rot" and self.rot != (0,0,0):
                self.tgtrot = zup_quat(line)
            if line.split()[0] == "dir":
                self.tgtdir = zup_tuple(line)

class link:
    """A link for a part for a ship lol"""
    def __init__(self,line):
        self.line = line
        self.part = None
        self.partNumber = None

        self.set_data(self.line)

    def set_data(self,line):
        self.part = line.split(" ")[2]                                          #"link = parachuteLarge_4293084050" -> "parachuteLarge_4293084050"
        self.partNumber = int(line.split("_")[1])                               #"link = parachuteLarge_4293084050" -> 4293084050 use this number to figure out parenting hierarchy (link and higher -> set as parent) need to set as a property


class attN:
    """An attN for a part for a ship lol"""
    def __init__(self,line):
        self.line = line
        self.loc = None
        self.part = None
        self.partNumber = None

        self.set_data(self.line)

    def set_data(self,line):
        self.loc = line.split(" ")[2].split(",")[0]                             #"attN = bottom,decoupler1-2_4293084002" -> "bottom" may need this info at some point
        self.part = line.split(" ")[2].split(",")[1]                            #"attN = bottom,decoupler1-2_4293084002" -> "decoupler1-2_4293084002" 
        self.partNumber = int(line.split("_")[1])                               #"attN = bottom,decoupler1-2_4293084002" -> 4293084002


class sym:
    """A sym for a part for a ship lol"""
    def __init__(self,line):
        self.line = line
        self.part = None
        self.partNumber = None

        self.set_data(self.line)

    def set_data(self,line):
        self.part = line.split(" ")[2]                                          #"sym = RCSBlock_4293083644" -> "RCSBlock_4293083644"
        self.partNumber = int(line.split("_")[1])                               #"sym = RCSBlock_4293083644" -> 4293083644 also move/rotate/scale symmetrical parts maybe?
        

class srfN:
    """A srfN for a part for a ship lol"""
    def __init__(self,line):
        self.line = line
        self.type = None
        self.part = None
        self.partNumber = None

        self.set_data(self.line)

    def set_data(self,line):
        self.type = line.split(" ")[2].split(",")[0]                            #"srfN = srfAttach,RCSTank1-2_4293083910" -> "srfAttach"
        self.part = line.split(" ")[2].split(",")[1]                            #"srfN = srfAttach,RCSTank1-2_4293083910" -> "RCSTank1-4293083910"
        self.partNumber = int(line.split("_")[1])                               #"srfN = srfAttach,RCSTank1-2_4293083910" -> 4293083910

