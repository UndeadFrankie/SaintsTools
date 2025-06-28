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
    noesis.logPopup() #Enable this to force open the debug logger each time the plugin is ran
    
    xboxMagic = 1447773511    
    platform = bs.readUInt()

    if platform == xboxMagic:
        noesis.logOutput("<?xml version=\"1.0\" encoding=\"utf-8\"?>" + '\n')
        noesis.logOutput("<PegDescription>" + '\n')     
        bs = NoeBitStream(data, NOE_BIGENDIAN)
        noesis.logOutput("	<BigEndian>" + "False" + "</BigEndian>" + '\n')
        magic = bs.readUInt() #Repeat the read of magic because we've reopened the file as bs again
        noesis.logOutput("	<Magic>" + "GEKV" + "</Magic>" + '\n')
        versionNum = bs.readShort()
        noesis.logOutput("	<Version>" + str(versionNum) + "</Version>" '\n')
        subVersionNum = bs.readShort()
        #noesis.logOutput("Version: v." + str(versionNum) + "." + str(subVersionNum) + '\n')
        noesis.logOutput("	<Unknown06>" + "0000" + "</Unknown06>" '\n')
        fileSize = bs.readUInt() #Size of .peg_xbox2 file
        noesis.logOutput("	<FileSize>" + str(fileSize) + "</FileSize>" '\n')
        datafileSize = bs.readUInt() #Size of .g_peg_xbox2 file
        noesis.logOutput("	<DataFileSize>" + str(datafileSize) + "</DataFileSize>" '\n')
        #noesis.logOutput("Peg Size: " + str(fileSize) + " G Peg Size: " + str(datafileSize) + '\n')
        entryCount = bs.readUShort()
        noesis.logOutput("	<EntryCount>" + str(entryCount) + "</EntryCount>" '\n')
        unknown12 = bs.readUShort()
        noesis.logOutput("	<Unknown12>" + "0000" + "</Unknown12>" '\n')
        frameCount = bs.readUShort() #frameCount is used for looping instead of entries because of animated textures. 1 entry could have multiple frames.
        noesis.logOutput("	<FrameCount>" + str(frameCount) + "</FrameCount>" '\n')
        #noesis.logOutput("Entry Count: " + str(entryCount) + " Frame Count: " + str(frameCount) + '\n')
        unknown16 = bs.readUShort()
        noesis.logOutput("	<Unknown16>" + "0000" + "</Unknown16>" '\n')
        noesis.logOutput("	<Entries>" + '\n')

        folderName = rapi.getDirForFilePath(rapi.getInputName())
        baseName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getInputName()))
        texFile = folderName + baseName + ".g_peg_xbox2"
        textureData = rapi.loadIntoByteArray(texFile)
        td = NoeBitStream(textureData, NOE_BIGENDIAN) #this handles opening the matching g_peg files based on the input peg file name.
        
        listOffsets = []
        listWidth = []
        listHeight = []
        listFormat = []
        listUnknownFlags = []
        listMipMapCount = []
        listSizes = []
        listFrames = []
        listNames = [] #Creating arrays to store important info in. This will later be retrieved and used to create NoeTexture.       

        for i in range(frameCount):
            offset = bs.readUInt() #Offset in g_peg to the start of current texture data.
            listOffsets.append(offset)
            #noesis.logOutput("Texture Offset: " + str(offset) + '\n')
            width = bs.readUShort()
            listWidth.append(width)
            height = bs.readUShort()
            listHeight.append(height)
            format = bs.readUShort() #Used to identify what compression textures use. 400 = DXT-1.
            listFormat.append(format)
            #noesis.logOutput("Texture Resolution: " + str(width) + "x" + str(height) + '\n' + " Format: " + str(format) + '\n')
            unknown0A = bs.readUShort()
            unknown0C = bs.readUInt()
            frames = bs.readUShort() #How many frames this texture has. For all static textures this should be 1.
            listFrames.append(frames)
            #noesis.logOutput("Frames: " + str(frames) + '\n')
            unknown12 = bs.readUInt()
            unknown16 = bs.readUInt()
            unknownFlags = bs.readByte()
            listUnknownFlags.append(unknownFlags)
            mipMapCount = bs.readByte()
            listMipMapCount.append(mipMapCount)
            size = bs.readUInt() #The size of the texture data in bytes (decimal).
            listSizes.append(size)
            #noesis.logOutput("Size: " + str(size) + '\n')
            unknown20 = bs.readUInt()
            unknown24 = bs.readUInt()
            unknown28 = bs.readUInt()
            unknown2C = bs.readUInt()
            
        for i in range (frameCount): #loop through the footer of the file, reading each name and storing it in listNames for later.
            textureName = bs.readString()[:-4] #[:-4] is to trim the .tga extension off the file but if there's issues with the filenames delete that part.
            listNames.append(textureName) 
            
        for i in range(frameCount):
            noesis.logOutput("		<Entry>" + '\n')
            noesis.logOutput("			<Name>" + str(listNames[i]) + ".tga" + "</Name>" '\n')
            noesis.logOutput("			<Frames>" + '\n')
            
            noesis.logOutput("				<Frame>" + '\n')
            
            noesis.logOutput("					<Offset>" + str(listOffsets[i]) + "</Offset>" + '\n')
            noesis.logOutput("					<Width>" + str(listWidth[i]) + "</Width>" + '\n')
            noesis.logOutput("					<Height>" + str(listHeight[i]) + "</Height>" + '\n')
            #noesis.logOutput("					<Format>" + str(listOffsets[i]) + "</Format>" + '\n')
            

            if (listFormat[i] == 400):
                texData = td.readBytes(listSizes[i])
                noesis.logOutput("					<Format>" + "DXT1" + "</Format>" + '\n')
                try:
                    texData = rapi.swapEndianArray(texData, 2)
                except:
                    noesis.logOutput("					<Unknown0A>" + "0000" + "</Unknown0A>" + '\n')
                    noesis.logOutput("					<Unknown0C>" + "00000000" + "</Unknown0C>" + '\n')
                    noesis.logOutput("					<Frames>" + str(listFrames[i]) + "</Frames>" + '\n')
                    noesis.logOutput("					<Unknown12>" + "00000000" + "</Unknown12>" + '\n')
                    noesis.logOutput("					<Unknown16>" + "00000000" + "</Unknown16>" + '\n')
                    noesis.logOutput("					<UnknownFlags1A>" + str(listUnknownFlags[i]) + "</UnknownFlags1A>" + '\n')
                    noesis.logOutput("					<MipmapCount>" + str(listMipMapCount[i]) + "</MipmapCount>" + '\n')
                    noesis.logOutput("					<Size>" + str(listSizes[i]) + "</Size>" + '\n')
                    noesis.logOutput("					<Unknown20>" + "00000000" + "</Unknown20>" + '\n')
                    noesis.logOutput("					<Unknown24>" + "00000000" + "</Unknown24>" + '\n')
                    noesis.logOutput("					<Unknown28>" + "00000000" + "</Unknown28>" + '\n')
                    noesis.logOutput("					<Unknown2C>" + "00000000" + "</Unknown2C>" + '\n')
                    noesis.logOutput("				</Frame>" + '\n')
                    noesis.logOutput("			</Frames>" + '\n')
                    noesis.logOutput("		</Entry>" + '\n')
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
            elif (listFormat[i] == 401):
                texData = td.readBytes(listSizes[i])
                noesis.logOutput("					<Format>" + "DXT3" + "</Format>" + '\n')
                try:
                    texData = rapi.swapEndianArray(texData, 2)
                except:
                    noesis.logOutput("					<Unknown0A>" + "0000" + "</Unknown0A>" + '\n')
                    noesis.logOutput("					<Unknown0C>" + "00000000" + "</Unknown0C>" + '\n')
                    noesis.logOutput("					<Frames>" + str(listFrames[i]) + "</Frames>" + '\n')
                    noesis.logOutput("					<Unknown12>" + "00000000" + "</Unknown12>" + '\n')
                    noesis.logOutput("					<Unknown16>" + "00000000" + "</Unknown16>" + '\n')
                    noesis.logOutput("					<UnknownFlags1A>" + str(listUnknownFlags[i]) + "</UnknownFlags1A>" + '\n')
                    noesis.logOutput("					<MipmapCount>" + str(listMipMapCount[i]) + "</MipmapCount>" + '\n')
                    noesis.logOutput("					<Size>" + str(listSizes[i]) + "</Size>" + '\n')
                    noesis.logOutput("					<Unknown20>" + "00000000" + "</Unknown20>" + '\n')
                    noesis.logOutput("					<Unknown24>" + "00000000" + "</Unknown24>" + '\n')
                    noesis.logOutput("					<Unknown28>" + "00000000" + "</Unknown28>" + '\n')
                    noesis.logOutput("					<Unknown2C>" + "00000000" + "</Unknown2C>" + '\n')
                    noesis.logOutput("				</Frame>" + '\n')
                    noesis.logOutput("			</Frames>" + '\n')
                    noesis.logOutput("		</Entry>" + '\n')
                    continue
                if (listSizes[i] != 0):
                    texData = rapi.imageUntile360DXT(texData, listWidth[i], listHeight[i], 16)
                    texData = rapi.imageDecodeDXT(texData, listWidth[i], listHeight[i], noesis.FOURCC_BC2)
                    texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))
                else:
                    noesis.logOutput("EMPTY TEXTURE")
                    continue
            elif (listFormat[i] == 402):
                texData = td.readBytes(listSizes[i])
                noesis.logOutput("					<Format>" + "DXT5" + "</Format>" + '\n')
                try:
                    texData = rapi.swapEndianArray(texData, 2)
                except:
                    noesis.logOutput("					<Unknown0A>" + "0000" + "</Unknown0A>" + '\n')
                    noesis.logOutput("					<Unknown0C>" + "00000000" + "</Unknown0C>" + '\n')
                    noesis.logOutput("					<Frames>" + str(listFrames[i]) + "</Frames>" + '\n')
                    noesis.logOutput("					<Unknown12>" + "00000000" + "</Unknown12>" + '\n')
                    noesis.logOutput("					<Unknown16>" + "00000000" + "</Unknown16>" + '\n')
                    noesis.logOutput("					<UnknownFlags1A>" + str(listUnknownFlags[i]) + "</UnknownFlags1A>" + '\n')
                    noesis.logOutput("					<MipmapCount>" + str(listMipMapCount[i]) + "</MipmapCount>" + '\n')
                    noesis.logOutput("					<Size>" + str(listSizes[i]) + "</Size>" + '\n')
                    noesis.logOutput("					<Unknown20>" + "00000000" + "</Unknown20>" + '\n')
                    noesis.logOutput("					<Unknown24>" + "00000000" + "</Unknown24>" + '\n')
                    noesis.logOutput("					<Unknown28>" + "00000000" + "</Unknown28>" + '\n')
                    noesis.logOutput("					<Unknown2C>" + "00000000" + "</Unknown2C>" + '\n')
                    noesis.logOutput("				</Frame>" + '\n')
                    noesis.logOutput("			</Frames>" + '\n')
                    noesis.logOutput("		</Entry>" + '\n')
                    continue
                if (listSizes[i] != 0):
                    texData = rapi.imageUntile360DXT(texData, listWidth[i], listHeight[i], 16)
                    texData = rapi.imageDecodeDXT(texData, listWidth[i], listHeight[i], noesis.FOURCC_BC3)
                    texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))
                else:
                    continue
            elif (listFormat[i] == 603):
                texData = td.readBytes(listSizes[i])
                noesis.logOutput("					<Format>" + "DXT1" + "</Format>" + '\n')
                try:
                    texData = rapi.swapEndianArray(texData, 2)
                except:
                    noesis.logOutput("					<Unknown0A>" + "0000" + "</Unknown0A>" + '\n')
                    noesis.logOutput("					<Unknown0C>" + "00000000" + "</Unknown0C>" + '\n')
                    noesis.logOutput("					<Frames>" + str(listFrames[i]) + "</Frames>" + '\n')
                    noesis.logOutput("					<Unknown12>" + "00000000" + "</Unknown12>" + '\n')
                    noesis.logOutput("					<Unknown16>" + "00000000" + "</Unknown16>" + '\n')
                    noesis.logOutput("					<UnknownFlags1A>" + str(listUnknownFlags[i]) + "</UnknownFlags1A>" + '\n')
                    noesis.logOutput("					<MipmapCount>" + str(listMipMapCount[i]) + "</MipmapCount>" + '\n')
                    noesis.logOutput("					<Size>" + str(listSizes[i]) + "</Size>" + '\n')
                    noesis.logOutput("					<Unknown20>" + "00000000" + "</Unknown20>" + '\n')
                    noesis.logOutput("					<Unknown24>" + "00000000" + "</Unknown24>" + '\n')
                    noesis.logOutput("					<Unknown28>" + "00000000" + "</Unknown28>" + '\n')
                    noesis.logOutput("					<Unknown2C>" + "00000000" + "</Unknown2C>" + '\n')
                    noesis.logOutput("				</Frame>" + '\n')
                    noesis.logOutput("			</Frames>" + '\n')
                    noesis.logOutput("		</Entry>" + '\n')
                    continue
                if (listSizes[i] != 0):
                    texData = rapi.imageUntile360DXT(texData, listWidth[i], listHeight[i], 8)
                    texData = rapi.imageDecodeDXT(texData, listWidth[i], listHeight[i], noesis.FOURCC_DXT1NORMAL)
                    texList.append(NoeTexture(listNames[i], listWidth[i], listHeight[i], texData, noesis.NOESISTEX_RGBA32))
                else:
                    continue
            else:
                noesis.logOutput("Texture Format Not Supported!" + '\n')
                continue
            
            noesis.logOutput("					<Unknown0A>" + "0000" + "</Unknown0A>" + '\n')
            noesis.logOutput("					<Unknown0C>" + "00000000" + "</Unknown0C>" + '\n')
            noesis.logOutput("					<Frames>" + str(listFrames[i]) + "</Frames>" + '\n')
            noesis.logOutput("					<Unknown12>" + "00000000" + "</Unknown12>" + '\n')
            noesis.logOutput("					<Unknown16>" + "00000000" + "</Unknown16>" + '\n')
            noesis.logOutput("					<UnknownFlags1A>" + str(listUnknownFlags[i]) + "</UnknownFlags1A>" + '\n')
            noesis.logOutput("					<MipmapCount>" + str(listMipMapCount[i]) + "</MipmapCount>" + '\n')
            noesis.logOutput("					<Size>" + str(listSizes[i]) + "</Size>" + '\n')
            noesis.logOutput("					<Unknown20>" + "00000000" + "</Unknown20>" + '\n')
            noesis.logOutput("					<Unknown24>" + "00000000" + "</Unknown24>" + '\n')
            noesis.logOutput("					<Unknown28>" + "00000000" + "</Unknown28>" + '\n')
            noesis.logOutput("					<Unknown2C>" + "00000000" + "</Unknown2C>" + '\n')
            
            noesis.logOutput("				</Frame>" + '\n')
            
            noesis.logOutput("			</Frames>" + '\n')
            noesis.logOutput("		</Entry>" + '\n')
        noesis.logOutput("	</Entries>" + '\n')
        noesis.logOutput("</PegDescription>" + '\n')  
                    
    return 1