#!/usr/bin/env python3

import argparse
import os
from datetime import datetime, timedelta
from hurry.filesize import size

import kotor.bif as bif
from kotor.tools import *

class RessourceType:
    def __init__(self, id, extension, description):
        self.id = id
        self.extension = extension
        self.description = description

    def __str__(self):
        return """RessourceType: {{id: ox{id:x}, extension: {extension}, description: {description}}}""".format(**vars(self))

ressourceTypeTable = {
    1: RessourceType(1, 'bmp', 'Windows BMP file'),
    3: RessourceType(3, 'tga', 'TGA image format'),
    4: RessourceType(4, 'wav', 'WAV sound file'),
    6: RessourceType(6, 'plt', 'Bioware Packed Layered Texture, used for player character skins, allows for multiple color layers'),
    7: RessourceType(7, 'ini', 'Windows INI file format'),
    10: RessourceType(10, 'txt', 'Text file'),
	11: RessourceType(11, 'wma', 'Audio, Windows media'),
	12: RessourceType(12, 'wmv', 'Video, Windows media'),
    2002: RessourceType(2002, 'mdl', 'Aurora model'),
    2009: RessourceType(2009, 'nss', 'NWScript Source'),
    2010: RessourceType(2010, 'ncs', 'NWScript Compiled Script'),
    2012: RessourceType(2012, 'are', 'BioWare Aurora Engine Area file. Contains information on what tiles are located in an area, as well as other static area properties that cannot change via scripting. For each .are file in a .mod, there must also be a corresponding .git and .gic file having the same ResRef.'),
    2013: RessourceType(2013, 'set', 'BioWare Aurora Engine Tileset'),
    2014: RessourceType(2014, 'ifo', 'Module Info File. See the IFO Format document.'),
    2015: RessourceType(2015, 'bic', 'Character/Creature'),
    2016: RessourceType(2016, 'wok', 'Walkmesh'),
    2017: RessourceType(2017, '2da', '2-D Array'),
    2022: RessourceType(2022, 'txi', 'Extra Texture Info'),
    2023: RessourceType(2023, 'git', 'Game Instance File. Contains information for all object instances in an area, and all area properties that can change via scripting.'),
    2025: RessourceType(2025, 'uti', 'Item Blueprint'),
    2026: RessourceType(2026, 'btc', 'Creature template (BioWare), GFF.'),
    2027: RessourceType(2027, 'utc', 'Creature template (user), GFF'),
    2029: RessourceType(2029, 'dlg', 'Conversation File'),
    2030: RessourceType(2030, 'itp', 'Tile/Blueprint Palette File'),
    2032: RessourceType(2032, 'utt', 'Trigger Blueprint'),
    2033: RessourceType(2033, 'dds', 'Compressed texture file'),
    2035: RessourceType(2035, 'uts', 'Sound Blueprint'),
    2036: RessourceType(2036, 'ltr', 'Letter-combo probability info for name generation'),
    2037: RessourceType(2037, 'gff', 'Generic File Format. Used when undesirable to create a new file extension for a resource, but the resource is a GFF. (Examples of GFFs include itp, utc, uti, ifo, are, git)'),
    2038: RessourceType(2038, 'fac', 'Faction File'),
    2040: RessourceType(2040, 'ute', 'Encounter Blueprint'),
    2042: RessourceType(2042, 'utd', 'Door Blueprint'),
    2044: RessourceType(2044, 'utp', 'Placeable Object Blueprint'),
    2045: RessourceType(2045, 'dft', 'Default Values file. Used by area properties dialog'),
    2046: RessourceType(2046, 'gic', 'Game Instance Comments. Comments on instances are not used by the game, only the toolset, so they are stored in a gic instead of in the git with the other instance properties.'),
    2047: RessourceType(2047, 'gui', 'Graphical User Interface layout used by game'),
    2051: RessourceType(2051, 'utm', 'Store/Merchant Blueprint'),
    2052: RessourceType(2052, 'dwk', 'Door walkmesh'),
    2053: RessourceType(2053, 'pwk', 'Placeable Object walkmesh'),
    2056: RessourceType(2056, 'jrl', 'Journal File'),
    2058: RessourceType(2058, 'utw', 'Waypoint Blueprint. See Waypoint GFF document.'),
    2060: RessourceType(2060, 'ssf', 'Sound Set File. See Sound Set File Format document'),
    2064: RessourceType(2064, 'ndb', 'Script Debugger File'),
    2065: RessourceType(2065, 'ptm', 'Plot Manager file/Plot Instance'),
    2066: RessourceType(2066, 'ptt', 'Plot Wizard Blueprint'),

	3000: RessourceType(3000, 'lyt', 'Area data, room layout.'),
	3001: RessourceType(3001, 'vis', 'Area data, room visibilities.'),
	3003: RessourceType(3003, 'pth', 'Pathfinder data. GFF.'),
	3007: RessourceType(3007, 'tpc', 'Texture.'),
    3008: RessourceType(3008, 'mdx','Geometry, model mesh data.')

}

class FileEntry:
    def __init__(self, file):
        self.size = read32(file)
        self.nameOffset = read32(file)
        self.nameSize = read16(file)
        self.drives = read16(file)

    def __str__(self):
        return """FileEntry: {{size: {size}, nameOffset: 0x{nameOffset:x}, nameSize: {nameSize}, name: {name}, drives: {drives}}}""".format(**vars(self))


class KeyEntry:
    def __init__(self, file):
        self.name = file.read(16).partition(b'\0')[0].decode("utf-8")
        resourceTypeId = read16(file)
        self.type = ressourceTypeTable.get(resourceTypeId, RessourceType(resourceTypeId, 'NA{}'.format(resourceTypeId), 'Invalid resource type'))
        self.id = read32(file)
        self.bifFile = self.id >> 20
        self.bifIndex = self.id & 0xFFFFF

    def __str__(self):
        return """KeyEntry: {{name: {name}, type: {type}, id: 0x{id:x}, bifFile: {bifFile}, bifIndex:0x{bifIndex:x}, bifName:{bifName}}}""".format(**vars(self))


class BuildDate:
    def __init__(self, year, days):
        self.date = datetime(1900+year, 1, 1) + timedelta(days - 1)

    def __str__(self):
        return self.date.strftime("%d.%m.%Y")


class Header:
    def __init__(self, file):
        self.marker = file.read(4).decode("utf-8")
        self.version = file.read(4).decode("utf-8")
        self.numFiles = readu32(file)
        self.numKeys = readu32(file)
        self.fileOffset = readu32(file)
        self.keyOffset = readu32(file)
        self.buildDate = BuildDate(readu32(file), readu32(file))
        readu32(file) # reserved

    def __str__(self):
        return """{name}: {{magic: "{marker}{version}", numFiles: {numFiles}, numKeys: {numKeys}, fileOffset: 0x{fileOffset:x}, keyOffset: 0x{keyOffset:x}, build: {buildDate}}}""".format(name=type(self).__name__, **vars(self))

class KeyFile:
    def __init__(self, path, header, entries, fileDirectory):
        self.path = path
        self.header = header
        self.entries = entries
        self.fileDirectory = fileDirectory

    def __str__(self):
        return """{name}: {{path: "{path}", header: {header}, #entries: {numEntries}}}""".format(name=type(self).__name__, path=self.path, header=self.header, numEntries=len(self.entries))


def list_bif_files(keyFile):
    # list bif files
    print ("{:>7} {:>7} {}".format('size', 'entries' , 'bif filename'))
    for entry in keyFile.entries:
        print ("{:>7} {:>7} {}".format(size(entry.size), len(keyFile.fileDirectory[entry.name]) , entry.name))

def get_absolute_bif_filename(keyFile, bifFile):
    path = os.path.dirname(keyFile.path)
    return os.path.join(path, bifFile)
    

def list_bif_contents(keyFile, bifFile):
    bifEntries = keyFile.fileDirectory[bifFile]
    bifPath =  get_absolute_bif_filename(keyFile, bifFile)
    bifDirectory = bif.read_bif_directory(bifPath)

    print ("{:>7} {:>7} {:>7} {}".format('index', 'size', 'filename', 'type'))

    for entry in bifEntries:
        print ("{:>7} {:>7} {}.{}".format(entry.bifIndex, bifDirectory[entry.bifIndex].size, entry.name , entry.type.extension))


def list_entries(parsed, keyFile):
    bifFile = parsed.bifFile
    if bifFile:
        if bifFile in keyFile.fileDirectory:
            list_bif_contents(keyFile, bifFile)
        else:
            print("error: bif file '{}' not found in {}".format(bifFile, keyFile.path))

    else:
        list_bif_files(keyFile)

def extract_entry(parsed, keyFile):
    bifFile = parsed.bifFile
    if not bifFile:
        print ("error: need to supply bif file")
        return
    if bifFile not in keyFile.fileDirectory:
        print("error: bif file '{}' not found in {}".format(bifFile, keyFile.path))
        return

    if not parsed.files:
        print("error: nothing to extract.")
        return

    bif_path = get_absolute_bif_filename(keyFile, bifFile)
    # read bif directory
    bifDirectory = bif.read_bif_directory(bif_path)
    # remove file extensions
    filesToExtract = [os.path.splitext(file)[0] for file in parsed.files]
    # find bifEntries for specified filenames
    bifEntries = keyFile.fileDirectory[bifFile]
    bifEntriesToExtract = [entry for entry in bifEntries if entry.name in filesToExtract]

    with open(bif_path, "rb") as bif_file:
        for entry in bifEntriesToExtract:
            with open("{}.{}".format(entry.name, entry.type.extension), "wb") as destination_file:
                bifEntry = bifDirectory[entry.bifIndex];
                for chunk in bif.read_bif_file (bif_file, bifEntry):
                    destination_file.write(chunk)




def checkEntryName(entry, filesToExtract):
    for file in filesToExtract:
        print (file, entry.name, type(file), type(entry.name), ":".join("{:02x}".format(ord(c)) for c in file), ":".join("{:02x}".format(ord(c)) for c in entry.name), len(file), len(entry.name))
        if file == entry.name:
            return True
    return False

def update_entry(parsed, keyFile):
    pass

def delete_entry(parsed, keyFile):
    pass


def execute_action(parsed, keyFile):
    switcher= {
        "list" : list_entries,
        "update" : update_entry,
        "extract" : extract_entry,
        "delete" : delete_entry
    }
    func = switcher.get(parsed.action, lambda: print("You need to specify one of -l, -u, -x, -d"))
    func(parsed, keyFile)

def readKeyDirectory(fileName):
    with open(fileName, "rb") as file:
        header = Header(file)

        # skip to start of File List Table and read File Header
        file.seek(header.fileOffset)
        entries = readlist(FileEntry, file, header.numFiles)
        # Read File Name for each entry
        for entry in entries:
            file.seek(entry.nameOffset)
            entry.name = file.read(entry.nameSize).partition(b'\0')[0].decode("utf-8").replace('\\', os.sep)

        # read all key entries
        file.seek(header.keyOffset)
        keyEntries = readlist(KeyEntry, file, header.numKeys)
        # sort key entries to bif files
        fileDirectory = {}
        for keyEntry in keyEntries:
            keyEntry.bifName = entries[keyEntry.bifFile].name
            if keyEntry.bifName not in fileDirectory:
                fileDirectory[keyEntry.bifName] = []
            fileDirectory[keyEntry.bifName].append(keyEntry)

        return KeyFile(fileName, header, entries, fileDirectory)

def parse_command_line():
    parser = argparse.ArgumentParser(description='Process KEY and BIF files.')
    parser.add_argument('keyFile', help='path to key file (i.e. chitinkey)')
    parser.add_argument('bifFile', nargs='?', help='bif file referenced from key file')
    parser.add_argument('files', nargs='*', help='file to extract, delete or update (without extension)')
    parser.add_argument('-l', action='store_const', dest='action', const='list', help='List contents of bif or key file')
    parser.add_argument('-x', action='store_const', dest='action', const='extract', help='Extract file <file> from bif file')
    parser.add_argument('-u', action='store_const', dest='action', const='update', help='Updates a file bif or key file (not yet implemented)')
    parser.add_argument('-d', action='store_const', dest='action', const='delete', help='Delete file <file> from bif file  (not yet implemented)')
    parser.add_argument('--dir', action='store', dest='directory', help='Directory from where to read or where to write to. Defaults to current directory.  (not yet implemented)')

    parsed = parser.parse_args()

    keyFile = readKeyDirectory(parsed.keyFile)
    execute_action(parsed, keyFile)


def main():
    parse_command_line()

if __name__ == "__main__":
    main()

