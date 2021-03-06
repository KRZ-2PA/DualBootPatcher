import multiboot.debug as debug
import multiboot.operatingsystem as OS

import imp
import os
import shutil


BOOT_IMAGE = 'img'
ZIP_FILE = 'zip'
UNSUPPORTED = 'UNSUPPORTED'


class FileInfo:
    def __init__(self):
        # Public (to be set by patchfile scripts)
        self.name = ''
        self.patch = None
        self.extract = None
        self.ramdisk = ""
        self.bootimg = "boot.img"
        self.has_boot_image = True
        self.loki = False
        self.device_check = True
        # Supported partition configurations
        self.configs = ['all']
        self.patched_init = None

        # Private
        self._device = None
        self._filename = None
        self._filetype = None # zip, img
        self._partconfig = None

    # Return the FileInfo object generated by a patchinfo script. The returned
    # object should not be changed. It should be merged info another FileInfo
    # object that has _filename set.
    def find_patchinfo(self):
        filename = os.path.split(self._filename)[1]

        searchpath = ['Google_Apps', 'Other']

        if self._device:
            searchpath.append(self._device)

        for i in searchpath:
            for root, dirs, files in os.walk(os.path.join(OS.patchinfodir, i)):
                for f in files:
                    if f.endswith(".py"):
                        plugin = imp.load_source(os.path.basename(f)[:-3],
                                                 os.path.join(root, f))
                        if plugin.matches(filename):
                            try:
                                file_info = plugin.get_file_info(filename=filename)
                            except:
                                file_info = plugin.get_file_info()

                            if file_info:
                                print('Detected ' + file_info.name)
                                return file_info

        return None

    def find_and_merge_patchinfo(self):
        other = self.find_patchinfo()

        if not other:
            return False

        self.name = other.name
        self.patch = other.patch
        self.extract = other.extract
        self.ramdisk = other.ramdisk
        self.bootimg = other.bootimg
        self.has_boot_image = other.has_boot_image
        self.loki = other.loki
        self.device_check = other.device_check
        self.configs = other.configs
        self.patched_init = other.patched_init

        return True

    def set_device(self, device):
        self._device = device

    def set_filename(self, filename):
        self._filename = filename
        extension = os.path.splitext(self._filename)[1]
        if extension == '.zip':
            self._filetype = ZIP_FILE
        elif extension == '.img':
            self._filetype = BOOT_IMAGE
        elif extension == '.lok':
            self._filetype = BOOT_IMAGE
        else:
            self._filetype = UNSUPPORTED

    def set_partconfig(self, partconfig):
        self._partconfig = partconfig

    def get_new_filename(self):
        fileext = os.path.splitext(self._filename)
        base = fileext[0] + '_' + self._partconfig.id
        return base + fileext[1]

    def move_to_target(self, newfile, move=False, delete=True):
        targetfile = self.get_new_filename()

        if os.path.exists(targetfile):
            os.remove(targetfile)

        if move:
            shutil.move(newfile, targetfile)
        else:
            shutil.copyfile(newfile, targetfile)
            if delete:
                os.remove(newfile)

    def is_filetype_supported(self):
        return self._filetype != UNSUPPORTED

    def is_partconfig_supported(self, partconfig):
        if (('all' not in self.configs
                and partconfig.id not in self.configs)
                or ('!' + partconfig.id) in self.configs):
            return False
        else:
            return True


def get_infos(device):
    infos = list()

    for i in ['Google_Apps', 'Other', device]:
        for root, dirs, files in os.walk(os.path.join(OS.patchinfodir, i)):
            for f in files:
                if f.endswith(".py"):
                    relpath = os.path.relpath(os.path.join(root, f), OS.patchinfodir)
                    plugin = imp.load_source(os.path.basename(f)[:-3],
                                             os.path.join(root, f))
                    file_info = plugin.get_file_info()

                    infos.append((relpath, file_info))

    return infos


def get_inits():
    initdir = os.path.join(OS.ramdiskdir, 'init')
    inits = list()

    for root, dirs, files in os.walk(initdir):
        for f in files:
            inits.append(os.path.relpath(os.path.join(root, f), initdir))

    # Newest first
    inits.sort()
    inits.reverse()

    return inits
