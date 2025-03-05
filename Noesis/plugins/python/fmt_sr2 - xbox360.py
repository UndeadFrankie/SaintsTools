from inc_noesis import *
import math

def registerNoesisTypes():
    handle = noesis.register("Saints Row 2 Texture Container (Xbox 360)", ".peg_xbox2")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1

def CheckType(data):
    bs = NoeBitStream(data)
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data, NOE_BIGENDIAN)
    rapi.processCommands("-texnorepfn") #Disable automatic texture renaming on export. 
    #noesis.logPopup() Enable this to force open the debug logger each time the plugin is ran
    
    xboxMagic = 1447773511    
    platform = bs.readUInt()

    if platform == xboxMagic:
        bs = NoeBitStream(data, NOE_BIGENDIAN)
        magic = bs.readUInt() #Repeat the read of magic because we've reopened the file as bs again
        versionNum = bs.readShort()
        subVersionNum = bs.readShort()
        noesis.logOutput("Version: v." + str(versionNum) + "." + str(subVersionNum) + '\n')
        fileSize = bs.readUInt() #Size of .peg_xbox2 file
        datafileSize = bs.readUInt() #Size of .g_peg_xbox2 file
        noesis.logOutput("Peg Size: " + str(fileSize) + " G Peg Size: " + str(datafileSize) + '\n')
        entryCount = bs.readUShort()
        unknown12 = bs.readUShort()
        frameCount = bs.readUShort() #frameCount is used for looping instead of entries because of animated textures. 1 entry could have multiple frames.
        noesis.logOutput("Entry Count: " + str(entryCount) + " Frame Count: " + str(frameCount) + '\n')
        unknown16 = bs.readUShort()        

        folderName = rapi.getDirForFilePath(rapi.getInputName())
        baseName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getInputName()))
        texFile = folderName + baseName + ".g_peg_xbox2"
        textureData = rapi.loadIntoByteArray(texFile)
        td = NoeBitStream(textureData, NOE_BIGENDIAN) #this handles opening the matching g_peg files based on the input peg file name.
        
        listOffsets = []
        listWidth = []
        listHeight = []
        listFormat = []
        listMipMapCount = []
        listSizes = []
        listFrames = []
        listNames = [] #Creating arrays to store important info in. This will later be retrieved and used to create NoeTexture.         

        for i in range(frameCount):        
            offset = bs.readUInt() #Offset in g_peg to the start of current texture data.
            #noesis.logOutput("Texture Offset: " + str(dataStart) + '\n')
            width = bs.readUShort()
            listWidth.append(width)
            height = bs.readUShort()
            listHeight.append(height)
            format = bs.readUShort() #Used to identify what compression textures use. 400 = DXT-1.
            listFormat.append(format)
            noesis.logOutput("Texture Resolution: " + str(width) + "x" + str(height) + '\n' + " Format: " + str(format) + '\n')
            unknown0A = bs.readUShort()
            unknown0C = bs.readUInt()
            frames = bs.readUShort() #How many frames this texture has. For all static textures this should be 1.
            noesis.logOutput("Frames: " + str(frames) + '\n')
            unknown12 = bs.readUInt()
            unknown16 = bs.readUInt()
            unknownFlags = bs.readByte()
            mipMapCount = bs.readByte()
            size = bs.readUInt() #The size of the texture data in bytes (decimal).
            listSizes.append(size)
            noesis.logOutput("Size: " + str(size) + '\n')
            unknown20 = bs.readUInt()
            unknown24 = bs.readUInt()
            unknown28 = bs.readUInt()
            unknown2C = bs.readUInt()
            
        for i in range (frameCount): #loop through the footer of the file, reading each name and storing it in listNames for later.
            textureName = bs.readString()[:-4] #[:-4] is to trim the .tga extension off the file but if there's issues with the filenames delete that part.
            listNames.append(textureName) 
            
        for i in range(frameCount):    
            if (listFormat[i] == 400):                    
                texData = td.readBytes(listSizes[i])
                noesis.logOutput("Texture Size: " + str(listSizes[i]) + '\n')
                try:
                    texData = rapi.swapEndianArray(texData, 2)
                except:
                    continue
                if (listSizes[i] != 0):
                    texData = rapi.imageUntile360DXT(texData, listWidth[i], listHeight[i], 8)
                    texData = rapi.imageDecodeDXT(texData, listWidth[i], listHeight[i], noesis.FOURCC_BC1)
                    texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))
                elif (listSizes[i] == 0):
                    continue
                else:
                    texData = td.readBytes(824)
                    texData = rapi.swapEndianArray(texData, 2)
                    texData = rapi.imageUntile360DXT(texData, listWidth[i], listHeight[i], 8)
                    texData = rapi.imageDecodeDXT(texData, listWidth[i], listHeight[i], noesis.FOURCC_BC1)
                    texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))                                    
            elif (listFormat[i] == 402):
                texData = td.readBytes(listSizes[i])
                try:
                    texData = rapi.swapEndianArray(texData, 2)
                except:
                    continue
                if (listSizes[i] != 0):
                    texData = rapi.imageUntile360DXT(texData, listWidth[i], listHeight[i], 16)
                    texData = rapi.imageDecodeDXT(texData, listWidth[i], listHeight[i], noesis.FOURCC_BC3)
                    texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))
                else:
                    continue
            elif (listFormat[i] == 603):
                texData = td.readBytes(listSizes[i])
                try:
                    texData = rapi.swapEndianArray(texData, 2)
                except:
                    continue
                if (listSizes[i] != 0):
                    texData = rapi.imageUntile360DXT(texData, listWidth[i], listHeight[i], 8)
                    texData = rapi.imageDecodeDXT(texData, listWidth[i], listHeight[i], noesis.FOURCC_DXT1NORMAL)
                    texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))
                else:
                    continue
            else:
                continue                    
                    
    return 1