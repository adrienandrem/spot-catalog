#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Author Adrien ANDRÉ <adr.andre@laposte.net>
#
#  2014-12-30T15:05:59-0300
#


import os, sys, re
import argparse

from shutil import copytree
from Image import Image
from Image import dateTimeFormat

SYS_ENCODING = sys.getfilesystemencoding()


DIM_FILE = "SCENE01/METADATA.DIM"
NULL = ''

isoDateTimeFormat = "%Y-%m-%dT%H:%M:%S"
dateFormat = "%Y-%m-%d"


def get_image_paths(dir, pattern = re.compile(r'GU_[0-9]{6}')):
    '''Retrieve list of every SPOT image directory.'''
    matches = []

    for root, dirnames, filenames in os.walk(dir):
        for dirname in filter(lambda name: pattern.match(name), dirnames):
            matches.append(os.path.join(root, dirname))

    return matches


def save_footprints(images, filename):
    f = open(filename, 'w')
    f.write("job;mission;k;j;date;instrument;sensor;shift;grid_ref;code;geometry\n")
    for image in images:
        job     = image.get_job()
        mission = image.get_mission()
        k       = image.get_k()
        j       = image.get_j()
        date    = image.get_date().strftime(isoDateTimeFormat)
        instrument = image.get_instrument()
        sensor     = image.get_sensor()
        shift      = image.get_shift() if image.get_shift() else NULL
        grid_ref   = "{0}-{1}".format(image.get_k(), image.get_j())
        code = "{0}{1}".format(image.get_id(), image.get_shift() if image.get_shift() else NULL)
        s    = list(code) ; s[17] = '0' ; s[18] = '0' ; code = "".join(s)
        wkt  = image.get_wkt()

        line = "{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10}\n".format(
                                              job,
                                              mission,
                                              k,
                                              j,
                                              date,
                                              instrument,
                                              sensor,
                                              shift,
                                              grid_ref,
                                              code,
                                              wkt)
        f.write(line)
    f.close()



def archive(source, target):
    '''Moves images to target building a directory tree according to metadata.'''

    print "Looking for images..."
    paths = get_image_paths(source)

    moves = []
    images = []
    print "Processing metadata..."
    step = 100.0/float(len(paths))
    processed = 0.0
    for path in paths:
        # Get metadata file
        metadata_file = os.path.join(path, DIM_FILE)
        #(jobId, k, j, date, sensor, sourceId) = getMetadata(metadata_file)
        image = Image(metadata_file)
        image.set_path(path)

        images.append(image)

        dir_target = os.path.join(target,
                                  "{0}-{1}".format(image.get_k(), image.get_j()),
                                  "SPOT{0}".format(image.get_mission()),
                                  "{0}".format(image.get_date().strftime(dateFormat)),
                                  "{0}{1}".format(image.get_id()[19:], image.get_shift() if image.get_shift() else NULL),
                                  "input"
                                  )

        moves.append((image.get_path(), dir_target))
        processed += step
        print "({0:.1f}%) Targeting {2} to {3}".format(processed, image.get_job(), image.get_path(), dir_target)

#    print "Archiving images..."
#    for move in moves:
#        print "Copying {0} to {1}".format(move[0], move[1])
#        copytree(move[0], move[1])


    print "Writing footprints..."
    save_footprints(images, os.path.join(target, "footprints.csv"))


    return 0


def main():
    '''Main function.

    Retrieves arguments: source and target directories.

    clear ; python catalog.py data/ archive/'''

    parser = argparse.ArgumentParser()
    # TODO: Manage 2 default (required) arguments source_dir and target_dir
    parser.add_argument("src", help="Directory to scan")
    parser.add_argument("trg", help="Output directory")
    args = parser.parse_args()

    dir_source = args.src
    dir_target = args.trg

    archive(dir_source, dir_target)

    return 0


if __name__ == "__main__":
    main()
