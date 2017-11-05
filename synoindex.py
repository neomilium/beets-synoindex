from beets.plugins import BeetsPlugin
from beets import config

import subprocess
import os

# Global variables with default values
#  These values can be overwrite by beets config file
debug = False

cmd_synoindex_add_file = ['dummycommand', '-a']
cmd_synoindex_add_dir  = ['dummycommand', '-A']
cmd_synoindex_del_file = ['dummycommand', '-d']
cmd_synoindex_del_dir  = ['dummycommand', '-D']
cmd_synoindex_get      = ['dummycommand', '-g', 'dummyfilename', '-t', 'music']
cmd_synoindex_move     = ['dummycommand', '-N']

# SynoIndex class
class SynoIndex(BeetsPlugin):
    def __init__(self):
        super(SynoIndex, self).__init__()
        self.register_listener('pluginload', self.loaded)
        self.register_listener('item_imported', self.item_imported)
        self.register_listener('album_imported', self.album_imported)
        self.register_listener('item_removed', self.item_removed)
        self.register_listener('item_moved', self.item_moved)
        self.config.add({
            u'debug': False,
            u'command': '/usr/syno/bin/synoindex'
        })

    def loaded(self):
        self._log.info('Plugin loaded!')
        global debug
        debug = config['synoindex']['debug'].get(bool)
        synoindex_command = config['synoindex']['command'].get()
        if debug: print 'SynoIndex plugin will use: ' + synoindex_command
        cmd_synoindex_add_item[0] = synoindex_command
        cmd_synoindex_add_album[0] = synoindex_command
        cmd_synoindex_del_file[0] = synoindex_command
        cmd_synoindex_del_dir[0] = synoindex_command
        cmd_synoindex_get[0] = synoindex_command
        cmd_synoindex_move[0] = synoindex_command

    def item_imported(self, lib, item):
        if debug: print 'item_imported: lib: ' + str(lib) + ' item: ' + str(item)
        synoindex_add_item(item['path'])

    def album_imported(self, lib, album):
        if debug: print 'album_imported: lib: ' + str(lib) + ' album: ' + str(album)
        synoindex_add_album(album['path'])

    def item_removed(self, item):
        if debug: print 'item_removed: item: ' + str(item)
        synoindex_del_file(item['path'])

    def item_moved(self, item, source, destination):
        if debug: print 'item_moved: destination: ' + destination
        if source == destination:
            if debug: print 'item_moved: same source and destination'
            """ This occurs when 'beet modify QUERY field=newvalue' """
            """ There is no dedicated function with 'synoindex' command to update metadatas for a file but a move with same destination and source works. """
            """ Unfortunatly, this also occurs when running 'beet move' or 'beet move -a', I think this case is a bug... """
            """ So, you will need to comment this line to speedup the process if you do a 'beet move' on whole music library but only some need to be updated... """
            synonindex_move(source, destination)
        else:
            if debug: print 'item_moved: item:' + str(item)
            #print 'item_moved: item: ' + str(item) + ' source: ' + source + ' destination: ' + destination
            synonindex_move(source, destination)

# Helper fcts
def quote(s):
    return '"'+s+'"'

def execute(cmd):
    if debug:
        print cmd
    subprocess.call(cmd)

# Helpers: construct full command, then execute it
def synoindex_get_info(filename):
    if os.path.exists(filename):
        if os.path.isfile(filename):
            cmd = list(cmd_synoindex_get)
            cmd[2] = quote(filename)
            execute(cmd)
        else:
            print 'Error: ' + quote(filename) + ' is not a file.'

def synoindex_add(filename):
    if os.path.exists(filename):
        if os.path.isdir(filename):
            cmd = list(cmd_synoindex_add_dir)
            cmd.append(quote(filename))
            execute(cmd)
        elif os.path.isfile(filename):
            cmd = list(cmd_synoindex_add_file)
            cmd.append(quote(filename))
            execute(cmd)
        else:
            print 'Error: ' + quote(filename) + ' is not a file or directory.'
    else:
        print 'Error: ' + quote(filename) + ' does not exist.'

def synoindex_del_file(filename):
    cmd = list(cmd_synoindex_del_file)
    cmd.append(quote(filename))
    execute(cmd)

def synoindex_del_dir(filename):
    cmd = list(cmd_synoindex_del_dir)
    cmd.append(quote(filename))
    execute(cmd)

def synonindex_move(source, destination):
    cmd = list(cmd_synoindex_move)
    cmd.append(quote(destination))
    cmd.append(quote(source))
    execute(cmd)
