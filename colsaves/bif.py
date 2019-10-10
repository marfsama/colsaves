#!/usr/bin/env python3

from kotor.tools import *

# size of byte chunks to read
CHUCK_SIZE = 4096

class FileEntry:
    def __init__(self, file):
        self.id = read32(file) & 0xFFFFF
        self.offset = read32(file)
        self.size = read32(file)
        self.type = read32(file)

    def __str__(self):
        return """FileEntry: {{id: {id}, offset: 0x{offset:x}, size: {size}, type: {type}}}""".format(**vars(self))

class Header:
    def __init__(self, file):
        self.marker = file.read(4).decode("utf-8")
        self.version = file.read(4).decode("utf-8")
        self.numVariableResources = readu32(file)
        self.numFixedResources = readu32(file)
        self.variableTableOffset = readu32(file)

    def __str__(self):
        return """{name}: {{magic: "{marker}{version}", numVariableResources: {numVariableResources}, numFixedResources: {numFixedResources}, variableTableOffset: 0x{variableTableOffset:x}}}""".format(name=type(self).__name__, **vars(self))


def read_bif_directory(fileName):
    with open(fileName, "rb") as file:
        header = Header(file)
        file.seek(header.variableTableOffset)
        entries = readlist(FileEntry, file, header.numVariableResources)        
        entriesMap = {entry.id:entry  for entry in entries }
        return entriesMap

def read_bif_file(bif_file, bif_file_entry):
    return read_partial_stream(bif_file, bif_file_entry.offset, bif_file_entry.size)

