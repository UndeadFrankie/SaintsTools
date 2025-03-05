from inc_noesis import *
import math

def registerNoesisTypes():
    handle = noesis.register("Saints Row 2 Texture Container (PC)", ".peg_pc")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1

def CheckType(data):
    bs = NoeBitStream(data)
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data, NOE_LITTLEENDIAN)
    rapi.processCommands("-texnorepfn") #Disable automatic texture renaming on export. 
    #noesis.logPopup() Enable this to force open the debug logger each time the plugin is ran
    
    pcMagic = 1447773511  
    platform = bs.readUInt()

    if platform == pcMagic:
        bs = NoeBitStream(data, NOE_LITTLEENDIAN)
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
        texFile = folderName + baseName + ".g_peg_pc"
        textureData = rapi.loadIntoByteArray(texFile)
        td = NoeBitStream(textureData, NOE_LITTLEENDIAN) #this handles opening the matching g_peg files based on the input peg file name.
        
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
            listOffsets.append(offset)
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
            
        for i in range (frameCount):
            textureName = bs.readString() #loop through the footer of the file, reading each name and storing it in listNames for later.
            listNames.append(textureName) #[:-4] is to trim the .tga extension off the file but if there's issues with the filenames delete that part.
            
        for i in range(frameCount):    
            if (listFormat[i] == 400):
                td.setOffset(listOffsets[i])
                texData = td.readBytes(listSizes[i])
                texData = rapi.imageDecodeRaw(texData, listWidth[i], listHeight[i], "R8G8B8A8")
                texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_DXT1))
            elif (listFormat[i] == 401):
                td.setOffset(listOffsets[i])
                texData = td.readBytes(listSizes[i])
                texData = rapi.imageDecodeRaw(texData, listWidth[i], listHeight[i], "R8G8B8A8")
                texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_DXT3))                
            elif (listFormat[i] == 402):
                td.setOffset(listOffsets[i])
                texData = td.readBytes(listSizes[i])
                texData = rapi.imageDecodeRaw(texData, listWidth[i], listHeight[i], "R8G8B8A8")
                texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_DXT5))        
            elif (listFormat[i] == 403):
                td.setOffset(listOffsets[i])
                texData = td.readBytes(listSizes[i])
                texData = rapi.imageDecodeRaw(texData, listWidth[i], listHeight[i], "R5G6B5")
                texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))
            elif (listFormat[i] == 404):
                td.setOffset(listOffsets[i])
                texData = td.readBytes(listSizes[i])
                texData = rapi.imageDecodeRaw(texData, listWidth[i], listHeight[i], "A1R5G5B5")
                texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))                
            elif (listFormat[i] == 405):
                td.setOffset(listOffsets[i])
                texData = td.readBytes(listSizes[i])
                texData = rapi.imageDecodeRaw(texData, listWidth[i], listHeight[i], "A4R4G4B4")
                texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))            
            elif (listFormat[i] == 406):
                td.setOffset(listOffsets[i])
                texData = td.readBytes(listSizes[i])
                texData = rapi.imageDecodeRaw(texData, listWidth[i], listHeight[i], "R8G8B8")
                texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))                 
            elif (listFormat[i] == 407):
                td.setOffset(listOffsets[i])
                texData = td.readBytes(listSizes[i])
                texData = rapi.imageDecodeRaw(texData, listWidth[i], listHeight[i], "A8R8G8B8")
                texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))            
            elif (listFormat[i] == 408):
                td.setOffset(listOffsets[i])
                texData = td.readBytes(listSizes[i])
                texData = rapi.imageDecodeRaw(texData, listWidth[i], listHeight[i], "V8U8")
                texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))            
            elif (listFormat[i] == 409):
                td.setOffset(listOffsets[i])
                texData = td.readBytes(listSizes[i])
                texData = rapi.imageDecodeRaw(texData, listWidth[i], listHeight[i], "CxV8U8")
                texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))            
            elif (listFormat[i] == 410):
                td.setOffset(listOffsets[i])
                texData = td.readBytes(listSizes[i])
                texData = rapi.imageDecodeRaw(texData, listWidth[i], listHeight[i], "A8")
                texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))            
            else:
                continue                    
                    
    return 1