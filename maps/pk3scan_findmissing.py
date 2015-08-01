"""
pk3scan

Usage:
    pk3scan.py scan <pk3dir> <texdir>

"""
import logging
import os
import re
import sys
from docopt import docopt
from pathlib import Path
from zipfile import ZipFile, BadZipfile


valid_texture_prefix = re.compile(r'(?!//|qer_editorimage).*', flags=re.IGNORECASE)  # not commented or editor image


def parse_shader(shader):
    result = set()
    for line in shader:
        line = line.decode('utf-8', 'ignore').strip()
        if line.endswith('/') or not line.startswith('textures'):
            continue
        result.add(line)
    return result

# def parse_shader_textures(shader):
#    texre = re.compile(r'(.)+ textures/[0-9a-z_-]+/[0-9a-z_-]+\.[a-z]+', flags=re.IGNORECASE)
#    textures = set()
#    for line in shader:
#        line = line.decode('utf-8', 'ignore').strip()
#        if texre.match(line):
#            tex = line.split(' textures')
#            textures.add('textures'+tex[1])
#    return textures
    
def parse_referenced_shader_textures(shader, bsp_refs):
    """
    Given a .shader file, returns the textures referenced from shader definitions. Only
    considers shader definitions used in the .bsp by checking bsp_refs.

    :param shader: a .shader file
    :param bsp_refs: shaders/textures referenced from the .bsp
    :return: the set of required textures
    """
    current_shader_def = None

    # regex for matching texture references (.tga or .jpg), excluding commented lines and editor images
    # texre = re.compile(r'(?!//|qer_editorimage)(.+) (textures/[0-9a-z_-]+/[0-9a-z_-]+\.(jpg|tga))+', flags=re.IGNORECASE)
    # texre2=re.compile(r'(?!//|qer_editorimage)(.*?)(textures/(?:\S+/)+[^ ]+\.(?:tga|jpg))+', flags=re.IGNORECASE)
    # these didnt work

    textures = set()
    for line in shader:
        line = line.decode('utf-8', 'ignore').strip()
        if not line.endswith('/') and line.startswith('textures'):
            if line in bsp_refs:
                current_shader_def = line
            else:
                current_shader_def = None
            continue
        if current_shader_def:
            if texre.match(line):
                tex = line.split(' textures')
                textures.add('textures'+tex[1])
    return textures

def get_textures(input):
    if valid_texture_prefix.match(input):
        return re.findall(u'textures/(?:\S+/)+[^ ]+\.(?:tga|jpg)', input)
    return None

def parse_bsp_references(bspfile):
    shaders = set()
    texre = re.compile(r'textures/[0-9a-z_-]+/[0-9a-z_-]+', flags=re.IGNORECASE)
    for line in bspfile:
        line = line.decode('ascii', 'ignore').strip()
        matches = texre.findall(line)
        if matches:
            for match in matches:
                shaders.add(match)
    return shaders    

def scan(pk3dir, texdir):
    """
    Scan a pk3 files in a folder

    Check for shader conflicts and build a report of texture usages.

    Args:
        pk3dir - Path to a directory containing pk3 files to scan
        texdir - Path to directory containing common texture packs
    """
    logger = logging.getLogger('scan')
    pk3path = Path(pk3dir)
    texpath = Path(texdir)

    if not pk3path.is_dir():
        logger.error('{} is not a valid directory'.format(pk3path))
        sys.exit(1)

    if not texpath.is_dir():
        logger.error('{} is not a valid directory'.format(texpath))
        sys.exit(1)
    
    logger.info("Using pk3dir: {}".format(", ".join([x.name for x in pk3path.glob('*.pk3')])))
    logger.info("Using texdir: {}".format(", ".join([x.name for x in texpath.glob('*.pk3')])))

    # Build an index of shaders and textures to check against. Store file extension separately
    textures = {}  # {'textures/bla/asd': [('file.pk3', 'tga'), ('file2.pk3', 'tga')], } 
    shaders = {} # {'textures/bla/asd': ['file.pk3']}
    for pk3file in texpath.glob('*.pk3'):
        pk3zip = ZipFile(str(pk3file))
        for name in pk3zip.namelist():
            if name.endswith('/'):
                continue
            elif name.endswith('.shader'):
                # open .shader file
                shader = pk3zip.open(name)
                for line in shader:
                    line = line.decode('utf-8', 'ignore').strip()
                    if line.endswith('/'):
                        continue
                    if line.startswith('textures'):
                        # this line defines a shader, store the pk3file's name
                        if line in shaders:
                            shaders[line].append(pk3file)
                        else:
                            shaders[line] = [pk3file]
            elif not name.endswith('.bsp'):
                match = re.match('(.+)\.(jpg|tga)$', name, flags=re.IGNORECASE)
                if match:
                    # this file is a .jpg or .tga texture, store filename/extension separately
                    texture_path, extension = match.groups()
                    if texture_path in textures:
                        textures[texture_path].append((pk3file, extension))
                    else:
                        textures[texture_path] = [(pk3file, extension)]
    
    # now check maps for missing shaders/textures
    for pk3file in pk3path.glob('*.pk3'):
        pk3zip = ZipFile(str(pk3file))
        mapfiles = [x for x in pk3zip.namelist() if x.endswith('.bsp')]  # .bsp files
        shaderfiles = [x for x in pk3zip.namelist() if x.endswith('.shader')]  # .shader files
        
        if not mapfiles or not shaderfiles:
            logger.info('pk3 {} is missing maps or shaders, skipping'.format(pk3file.name))
            continue
        
        # store textures defined in this pk3
        pk3_texture_defs = [x for x in pk3zip.namelist() if x not in mapfiles and x not in shaderfiles]
        
        # store shaders defined in this pk3
        pk3_shader_defs = reduce(lambda x, y: x|y, [
            parse_shader(pk3zip.open(shaderfile)) for shaderfile in shaderfiles
        ])
        
        # store shaders/textures referenced in this pk3's .bsp files
        bsp_refs = reduce(lambda x, y: x|y, [
            parse_bsp_references(pk3zip.open(mapfile)) for mapfile in mapfiles
        ])
        
        # store textures referenced in this pk3's .shader files (skip non-used shader definitions)
        shader_texture_refs = reduce(lambda x, y: x|y, [
            parse_referenced_shader_textures(pk3zip.open(shaderfile), bsp_refs)
            for shaderfile in shaderfiles
        ])
        
        found_textures = 0
        missing_textures = 0
        missing_textures_found = 0
        for texref in shader_texture_refs:
            if texref not in pk3_texture_defs:
                foundin = ""
                if texref in textures.keys():
                    foundin = " -> found in {}".format(", ".join([x.name for x in textures[texref]]))
                    missing_textures_found += 1
                else:
                    missing_textures += 1
                logger.warning("{} misses texture {}{}".format(pk3file.name, texref, foundin))
            else:
                found_textures += 1
        
        found_shaders = 0
        missing_shaders = 0
        missing_shaders_found = 0
        for bsp_ref in bsp_refs:
            if bsp_ref not in pk3_shader_defs:
                foundin = ""
                if bsp_ref in shaders.keys():
                    foundin = " -> found in {}".format(", ".join([x.name for x in shaders[bsp_ref]]))
                    missing_shaders_found += 1
                else:
                    missing_shaders += 1
                logger.warning("{} misses shader {}{}".format(pk3file.name, bsp_ref, foundin))
            else:
                found_shaders += 1
        logger.info("--- Results for {}\n- Textures (based on the {} referenced & found shaders in pk3)\n\tReferenced: {}\n\tFound in pk3: {}\n\tMissing but found in data/texture pk3's: {}\n\tMISSING: {}\n"\
                                        "- Shaders\n\tReferenced: {}\n\tFound in pk3: {}\n\tMissing but found in data/texture pk3's: {}\n\tMISSING: {}\n---".format(
                        pk3file.name, found_shaders, len(shader_texture_refs), found_textures, missing_textures_found, missing_textures,
                        len(bsp_refs), found_shaders, missing_shaders_found, missing_shaders))
    logger.info("\nDone. Used texdir: {}".format(", ".join([x.name for x in texpath.glob('*.pk3')])))

def main():
    """Utilities Main method"""
    args = docopt(__doc__)
    if args['scan']:
        scan(args['<pk3dir>'], args['<texdir>'])

if __name__ == '__main__':
    logging.basicConfig(filename='pk3scan.log', level=logging.DEBUG)
    _CONLOG = logging.StreamHandler()
    _CONLOG.setLevel(logging.INFO)
    logging.getLogger('').addHandler(_CONLOG)
    main()
