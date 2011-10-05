#!/usr/bin/env python
#
# Copyright (c) 2011 Greek Research and Technology Network
#
"""Personalize an Image by injecting files

This hook injects files into the filesystem of an Image.
The files are passed to the hook through the Ganeti
OS interface and found in the variable OSP_IMG_PERSONALITY.

"""

import sys
import os
import json
import datetime
import base64


def timestamp():
    now = datetime.datetime.now()
    current_time = now.strftime("%Y%m%d.%H%M%S")
    return current_time


def main():
    if os.environ.has_key('SNF_IMAGE_PERSONALITY'):
        osp_img_personality = os.environ['SNF_IMAGE_PERSONALITY']
        files = json.loads(osp_img_personality)
        for f in files:
            if os.path.lexists(f['path']):
                backup_file = f['path'] + '.bak.' + timestamp()
                os.rename(f['path'],backup_file)
            file = file(f['path'], 'w')
            file.write(base64.b64decode(f['contents']))
            file.close()
            os.chmod(f['path'],0440)
        sys.stderr.write('Successful personalization of Image')
    else:
        sys.stderr.write('This Image has no personality (0 files to inject)')
    return 0


if __name__ == "__main__":
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
