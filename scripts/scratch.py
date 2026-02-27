
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
import arcgis
from arcgis.gis import GIS
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


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## Sign In to ArcGIS Online ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nSign In to ArcGIS Online")

gis = GIS(url=None, username = os.getenv("AGO_USERNAME"), password = os.getenv("AGO_PASSWORD"))
item = gis.content.get('cfcb7609de5f478eb7666240902d4d3d')
# Add the item to the arcgis pro geodatabase

# Path to your ArcGIS Pro project
aprx = arcpy.mp.ArcGISProject(prj_dirs["gis_folder_aprx"])
gdb_path = prj_dirs["gis_folder_gdb"]
arcpy.env.workspace = gdb_path
arcpy.env.overwriteOutput = True

# Select the map you want to add the layer to
m = aprx.listMaps("Map")[0]

# Remove all the rasters from the map
for lyr in m.listLayers():
    if lyr.isRasterLayer:
        m.removeLayer(lyr)

# Delete all rasters from the geodatabase
for raster in arcpy.ListRasters():
    arcpy.management.Delete(raster)


# ArcGIS Online Feature Service URL
layer_url = "https://ic.imagery1.arcgis.com/arcgis/rest/services/Sentinel2_10m_LandCover/ImageServer"

# Add the layer from the URL
hls_lyr = m.addDataFromPath(layer_url)

# Save changes
aprx.save()
print("Layer added successfully!")

oc_lyr = m.listLayers(wildcard = "OC Boundaries")[0]

hls_year = ['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']

# "https://www.arcgis.com/home/item.html?id=cfcb7609de5f478eb7666240902d4d3d"
image_server = r"https://ic.imagery1.arcgis.com/arcgis/rest/services/Sentinel2_10m_LandCover/ImageServer"
years = range(2017, 2025)

year = "2017"
where = f"Year = {year}"

lyr = "hls_2017"
arcpy.management.MakeImageServerLayer(
    image_server,
    lyr,
    where_clause = where,
    mosaic_method = "ByAttribute"
)

arcpy.management.Clip(
    in_raster = lyr,
    out_raster = os.path.join(gdb_path, f"hls{year}"),
    in_template_dataset = oc_lyr,
    nodata_value = "255",
    clipping_geometry = "NONE",
    maintain_clipping_extent="NO_MAINTAIN_EXTENT"
)


with arcpy.EnvManager(scratchWorkspace = gdb_path):
    out_raster = arcpy.sa.ExtractByMask(
        in_raster = os.path.join(gdb_path, f"hls{year}"),
        in_mask_data=os.path.join(gdb_path, "oc_boundaries"),
        extraction_area="INSIDE",
    )
    out_raster.save(os.path.join(gdb_path, f"ochls{year}"))

# Delete intermediate raster
arcpy.management.Delete(os.path.join(gdb_path, f"hls{year}"))

# Save changes
aprx.save()





sel_raster = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view = hls_lyr,
    selection_type = "NEW_SELECTION",
    where_clause = "ProductName = '2017'",
    invert_where_clause = None
)


arcpy.management.Clip(
    in_raster = sel_raster,
    out_raster = os.path.join(gdb_path, f"hls_2017"),
    in_template_dataset = oc_lyr,
    nodata_value = "255",
    clipping_geometry = "NONE",
    maintain_clipping_extent="NO_MAINTAIN_EXTENT"
)






for year in hls_year:
    print(f"Processing HLS for year {year}...")
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view = hls_lyr,
        selection_type="NEW_SELECTION",
        where_clause = f"ProductName = '{year}'",
        invert_where_clause=None
    )

    arcpy.management.Clip(
        in_raster = hls_lyr,
        out_raster = os.path.join(gdb_path, f"hls_{year}"),
        in_template_dataset = oc_lyr,
        nodata_value = "255",
        clipping_geometry = "NONE",
        maintain_clipping_extent="NO_MAINTAIN_EXTENT"
    )

    with arcpy.EnvManager(scratchWorkspace = gdb_path):
        out_raster = arcpy.sa.ExtractByMask(
            in_raster = os.path.join(gdb_path, f"hls_{year}"),
            in_mask_data=os.path.join(gdb_path, "oc_boundaries"),
            extraction_area="INSIDE",
        )
        out_raster.save(os.path.join(gdb_path, f"ochls_{year}"))

    # Delete intermediate raster
    arcpy.management.Delete(os.path.join(gdb_path, f"hls_{year}"))



for raster in arcpy.ListRasters():
    # Add the raster to the map
    raster_lyr = m.addDataFromPath(os.path.join(gdb_path, raster))
    print(f"Added raster layer: {raster}")

# Remove the original HLS layer
m.removeLayer(hls_lyr)

# Save changes
aprx.save()
print("Layer added successfully!")


for lyr in m.listLayers():
    print(lyr.name)

arcpy.ListFeatureClasses()
arcpy.ListRasters()


# Clear the selection
arcpy.management.SelectLayerByAttribute(
    in_layer_or_view = hls_lyr,
    selection_type="CLEAR_SELECTION",
    where_clause = None,
    invert_where_clause=None
)

