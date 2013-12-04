from fileinfo import FileInfo
import common as c
import re

file_info = FileInfo()

filename_regex           = r"^j(ged|f)lte([a-z]+)?-faux123-GE-.*\.zip$"
file_info.ramdisk        = 'jflte/GoogleEdition/GoogleEdition.def'
file_info.patch          = c.auto_patch
file_info.extract        = c.files_to_auto_patch

def matches(filename):
  if re.search(filename_regex, filename):
    return True
  else:
    return False

def print_message():
  print("Detected faux Google Edition kernel zip")

def get_file_info():
  return file_info