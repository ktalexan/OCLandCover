# -*- coding: utf-8 -*-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Project: OCHLS (Orange County Harmonized Landsat Sentinel v2)
# Part 1: Raw Data Processing ----
# Author: Dr. Kostas Alexandridis, GISP
# Version: 2026.1, Date: January 2026
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nOCHLS: Part 1 - Raw Data Processing\n")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Import necessary libraries ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1. Import necessary libraries")

import os
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
import arcgis
from ochls import HLSv2

# Load environment variables from .env file
load_dotenv()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Create project metadata and directories ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2. Create project metadata and directories")

# Initialize the OCHLS class
hls = HLSv2(part = 1, version = 2026.1)

# Create project variables
part = hls.part
version = hls.version

# Create project metadata
prj_meta = hls.prj_meta

# Create project directories
prj_dirs = hls.prj_dirs

# Create logger
logger = hls.logger

# Get the Coordinate Reference System (CRS) and Spatial Resolution (SR) from the HLS class
sr = hls.sr
# print(sr.factoryCode)

# Login to ArcGIS Online
arcgis.env.active_gis = arcgis.GIS("home")

gdb_path = prj_dirs["gis_folder_gdb"]
arcpy.env.workspace = gdb_path
arcpy.env.overwriteOutput = True


arcpy.ListFeatureClasses(feature_type = "Polygon")

gdb_md = md.Metadata(gdb_path)
print(gdb_md.title)

"Sentinel-2 10m Land Use/Land Cover Time Series"
"https://ic.imagery1.arcgis.com/arcgis/services/Sentinel2_10m_LandCover/ImageServer"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Sign in to ArcGIS Online (ArcPy + ArcGIS API for Python) and search for layer
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
portal_url = "https://www.arcgis.com"
try:
	# This will use ArcGIS Pro credentials or prompt for sign-in if needed
	arcpy.SignInToPortal(portal_url)
	print("Signed in to portal via arcpy.")
except Exception as e:
	print("arcpy.SignInToPortal failed or not available:", e)

# Ensure the ArcGIS API has an authenticated GIS instance
try:
	gis = arcgis.env.active_gis if arcgis.env.active_gis else arcgis.GIS(portal_url)
except Exception:
	# Fallback to home (uses stored credentials in ArcGIS Pro/ArcGIS API config)
	gis = arcgis.GIS("home")

search_url = "https://ic.imagery1.arcgis.com/arcgis/rest/services/Sentinel2_10m_LandCover/ImageServer"
print(f"Searching ArcGIS Online for items with URL: {search_url}")
items = []
try:
		# First attempt: search Living Atlas for the exact URL
		la_query = f'url:"{search_url}" AND source:"Living Atlas"'
		print(f"Searching Living Atlas with query: {la_query}")
		la_items = gis.content.search(la_query, item_type="Image Service", max_items=20)
		if la_items:
			items = la_items
		else:
			# Fallback: search ArcGIS Online by URL (Image Service preferred)
			print("No Living Atlas matches; falling back to ArcGIS Online URL search")
			items = gis.content.search(f'url:"{search_url}"', item_type="Image Service", max_items=20)
			if not items:
				items = gis.content.search(f'url:"{search_url}"', max_items=20)
except Exception as e:
	print("Search failed:", e)

if items:
	print(f"Found {len(items)} item(s):")
	for it in items:
		print(f"- Title: {it.title}")
		print(f"  ID: {it.id}")
		try:
			print(f"  URL: {it.url}")
		except Exception:
			print(f"  URL: (not available)")
		print(f"  Type: {it.type}")
		print("")
else:
	print("No matching items found on ArcGIS Online.")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# End of Script ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nLast Execution:", datetime.datetime.now().strftime("%Y-%m-%d"))
print("End of Script")
