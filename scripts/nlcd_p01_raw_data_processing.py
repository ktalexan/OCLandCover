# -*- coding: utf-8 -*-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Project: OCNLCD (Orange County National Land Cover Database)
# Part 1: Raw Data Processing ----
# Author: Dr. Kostas Alexandridis, GISP
# Version: 2026.1, Date: March 2026
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nOCNLCD: Part 1 - Raw Data Processing\n")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Import necessary libraries ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1. Import necessary libraries")

import os
import sys
import datetime
import json
import re
import logging
import unicodedata
from typing import Union, Optional, Dict, Any
import wmi
import pytz
import pandas as pd
from dotenv import load_dotenv
import arcpy
from arcpy import metadata as md
from arcgis.features import GeoAccessor, GeoSeriesAccessor
# import arcgis
# from arcgis.gis import GIS
from scripts.oclc import OCNLCD

# Load environment variables from .env file
load_dotenv()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Create project metadata and directories ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2. Create project metadata and directories")

# Initialize the OCNLCD class
nlcd = OCNLCD(part = 1, version = 2026.1)

# Create project variables
part = nlcd.part
version = nlcd.version

# Create project metadata
prj_meta = nlcd.prj_meta

# Create project directories
prj_dirs = nlcd.prj_dirs

# Create logger
logger = nlcd.logger

# Get the Coordinate Reference System (CRS) and Spatial Resolution (SR) from the NLCD class
sr = nlcd.sr
# print(sr.factoryCode)

# Get the codebook information for the NLCD service
cb_url = nlcd.cb_url


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## Process NLCD Databases ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nProcessing NLCD Databases")


### Process the land cover data ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Log and process the land cover data
# logger.enable(meta = prj_meta, filename = "NLCD_land_cover_processing.log", replace = True)
# print("NLCD Land Cover Processing Log\n")
# nlcd.process_service_data("land_cover")
# print("\nNLCD Land Cover processing completed. Check the log file for details.")
# logger.disable()


### Process the land cover change data ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Log and process the land cover change data
# logger.enable(meta = prj_meta, filename = "NLCD_land_cover_change_processing.log", replace = True)
# print("NLCD Land Cover Change Processing Log\n")
# nlcd.process_service_data("land_cover_change")
# print("\nNLCD Land Cover Change processing completed. Check the log file for details.")
# logger.disable()


### Process the land cover confidence data ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Log and process the land cover confidence data
# logger.enable(meta = prj_meta, filename = "NLCD_land_cover_confidence_processing.log", replace = True)
# print("NLCD Land Cover Confidence Processing Log\n")
# nlcd.process_service_data("land_cover_confidence")
# print("\nNLCD Land Cover Confidence processing completed. Check the log file for details.")
# logger.disable()


### Process the impervious surface data ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Log and process the impervious surface data
# logger.enable(meta = prj_meta, filename = "NLCD_impervious_surface_processing.log", replace = True)
# print("NLCD Impervious Surface Processing Log\n")
# nlcd.process_service_data("impervious_surface")
# print("\nNLCD Impervious Surface processing completed. Check the log file for details.")
# logger.disable()


### Process the fractional impervious surface data ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Log and process the fractional impervious surface data
# logger.enable(meta = prj_meta, filename = "NLCD_fractional_impervious_surface_processing.log", replace = True)
# print("NLCD Fractional Impervious Surface Processing Log\n")
# nlcd.process_service_data("fractional_impervious_surface")
# print("\nNLCD Fractional Impervious Surface processing completed. Check the log file for details.")
# logger.disable()


### Process the impervious descriptor data ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Log and process the impervious descriptor data
# logger.enable(meta = prj_meta, filename = "NLCD_impervious_descriptor_processing.log", replace = True)
# print("NLCD Impervious Descriptor Processing Log\n")
# nlcd.process_service_data("impervious_descriptor")
# print("\nNLCD Impervious Descriptor processing completed. Check the log file for details.")
# logger.disable()


### Process the date spectral change data ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Log and process the date spectral change data
# logger.enable(meta = prj_meta, filename = "NLCD_date_spectral_change_processing.log", replace = True)
# print("NLCD Date Spectral Change Processing Log\n")
# nlcd.process_service_data("date_spectral_change")
# print("\nNLCD Date Spectral Change processing completed. Check the log file for details.")
# logger.disable()


### Process the tree canopy cover data ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Log and process the tree canopy cover data
# logger.enable(meta = prj_meta, filename = "NLCD_tree_canopy_cover_processing.log", replace = True)
# print("NLCD Tree Canopy Cover Processing Log\n")
# nlcd.process_service_data("tree_canopy_cover")
# print("\nNLCD Tree Canopy Cover processing completed. Check the log file for details.")
# logger.disable()



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# End of Script ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nLast Execution:", datetime.datetime.now().strftime("%Y-%m-%d"))
print("End of Script")
