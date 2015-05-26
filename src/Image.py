#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 12:34:20 2015

@author: Author Adrien ANDRÉ <adr.andre@laposte.net>
"""


import xml.etree.ElementTree as ET
import datetime

dateTimeFormat = "%Y-%m-%d %H:%M:%S"


class Image(object):

    def __init__(self, dim_file):
        '''Recuperation des metadonnees dans un fichier XML METADATA.DIM.'''
        # TODO: Try method that does not load entire XML tree (SAX ?).
        # See: https://docs.python.org/2/library/pyexpat.html#module-xml.parsers.expat

        tree = ET.parse(dim_file) # "Parsing" : Construction d'un objet Python contenant la structure du fichier XML
        root = tree.getroot() # Racine du document

        job              = root.find("./Production/JOB_ID").text # "GU_004054"
        missionStr       = root.find("./Dataset_Sources/Source_Information/Scene_Source/MISSION_INDEX").text # "5"
        gridReferenceStr = root.find("./Dataset_Sources/Source_Information/Scene_Source/GRID_REFERENCE").text # "687340"
        shiftStr         = root.find("./Dataset_Sources/Source_Information/Scene_Source/SHIFT_VALUE").text
        imagingDateStr   = root.find("./Dataset_Sources/Source_Information/Scene_Source/IMAGING_DATE").text # "2013-09-11"
        imagingTimeStr   = root.find("./Dataset_Sources/Source_Information/Scene_Source/IMAGING_TIME").text # "13:36:53"
        instrumentStr    = root.find("./Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT_INDEX").text # "1"
        sensorStr        = root.find("./Dataset_Sources/Source_Information/Scene_Source/SENSOR_CODE").text # "A"
        id               = root.find("./Dataset_Sources/Source_Information/SOURCE_ID").text # "56873431407141336461A"

        self.points = []
        for corner in [0, 1, 2, 3]:
            lon = root.find("./Dataset_Frame/Vertex[{0}]/FRAME_LON".format(corner)).text
            lat = root.find("./Dataset_Frame/Vertex[{0}]/FRAME_LAT".format(corner)).text
            self.points.append((lon, lat))


        splitIndex = len(gridReferenceStr)/2

        self.job = job
        self.mission = int(missionStr)
        self.k = int(gridReferenceStr[:splitIndex])
        self.j = int(gridReferenceStr[splitIndex:])
        self.date = datetime.datetime.strptime("{0} {1}".format(imagingDateStr, imagingTimeStr), dateTimeFormat)
        self.instrument = int(instrumentStr)
        self.sensor = sensorStr
        self.shift = int(shiftStr) # if shiftStr else 0

        self.id = id


    def set_path(self, path):
        self.path = path

    def get_path(self):
        return self.path

    def get_job(self):
        return self.job

    def get_mission(self):
        return self.mission

    def get_shift(self):
        return self.shift

    def get_k(self):
        return self.k

    def get_j(self):
        return self.j

    def get_sensor(self):
        return self.sensor

    def get_date(self):
        return self.date

    def get_instrument(self):
        return self.instrument

    def get_id(self):
        return self.id

    def get_points(self):
        return self.points

    def get_wkt(self):
        points = self.get_points()
        points.append(self.get_points()[0])

        pointStr = ["{0} {1}".format(point[0], point[1]) for point in points]

        return "POLYGON (({0}))".format(", ".join(pointStr))


    def __repr__(self):
        footprint = self.id
        return footprint

    def __hash__(self):
        return hash(self.__repr__())

    def __str__(self):
        return self.__repr__()
