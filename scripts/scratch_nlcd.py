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
## Sign In to ArcGIS Online ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nSign In to ArcGIS Online")

# gis = GIS(url=None, username = os.getenv("AGO_USERNAME"), password = os.getenv("AGO_PASSWORD"))
# item = gis.content.get('cfcb7609de5f478eb7666240902d4d3d')
# Add the item to the arcgis pro geodatabase

aprx = arcpy.mp.ArcGISProject(prj_dirs["gis_ocnlcd_aprx"])

service_name = "tree_canopy_cover"
service_gdb = os.path.join(prj_dirs["gis_ocnlcd"], cb_url[service_name]["database"])
arcpy.env.workspace = service_gdb
arcpy.env.overwriteOutput = True
service_map = service_name + "_map"
if service_map not in [m.name for m in aprx.listMaps()]:
    # Create a new map for the service
    m = aprx.createMap(service_map)
    m.addBasemap("Topographic")
else:
    # Get the existing map for the service
    m = aprx.listMaps(service_map)[0]
m.openView()
print("\nAdding processed rasters to the map...")
for raster in arcpy.ListRasters():
    print(f"- Adding raster {raster} to the map...")
    # Add the raster to the map
    m.addDataFromPath(os.path.join(service_gdb, raster))
aprx.closeViews("MAPS")
aprx.save()



# Process the land cover data
logger.enable(meta = prj_meta, filename = "NLCD_land_cover_processing.log", replace = True)
print("NLCD Land Cover Processing Log\n")
nlcd.process_service_data("land_cover")
print("\nNLCD Land Cover processing completed. Check the log file for details.")
logger.disable()

# Process the land cover change data
logger.enable(meta = prj_meta, filename = "NLCD_land_cover_change_processing.log", replace = True)
print("NLCD Land Cover Change Processing Log\n")
nlcd.process_service_data("land_cover_change")
print("\nNLCD Land Cover Change processing completed. Check the log file for details.")
logger.disable()

# Process the land cover confidence data
logger.enable(meta = prj_meta, filename = "NLCD_land_cover_confidence_processing.log", replace = True)
print("NLCD Land Cover Confidence Processing Log\n")
nlcd.process_service_data("land_cover_confidence")
print("\nNLCD Land Cover Confidence processing completed. Check the log file for details.")
logger.disable()

# Process the impervious surface data
logger.enable(meta = prj_meta, filename = "NLCD_impervious_surface_processing.log", replace = True)
print("NLCD Impervious Surface Processing Log\n")
nlcd.process_service_data("impervious_surface")
print("\nNLCD Impervious Surface processing completed. Check the log file for details.")
logger.disable()

# Process the fractional impervious surface data
logger.enable(meta = prj_meta, filename = "NLCD_fractional_impervious_surface_processing.log", replace = True)
print("NLCD Fractional Impervious Surface Processing Log\n")
nlcd.process_service_data("fractional_impervious_surface")
print("\nNLCD Fractional Impervious Surface processing completed. Check the log file for details.")
logger.disable()

# Process the impervious descriptor data
logger.enable(meta = prj_meta, filename = "NLCD_impervious_descriptor_processing.log", replace = True)
print("NLCD Impervious Descriptor Processing Log\n")
nlcd.process_service_data("impervious_descriptor")
print("\nNLCD Impervious Descriptor processing completed. Check the log file for details.")
logger.disable()

# Process the date spectral change data
logger.enable(meta = prj_meta, filename = "NLCD_date_spectral_change_processing.log", replace = True)
print("NLCD Date Spectral Change Processing Log\n")
nlcd.process_service_data("date_spectral_change")
print("\nNLCD Date Spectral Change processing completed. Check the log file for details.")
logger.disable()

# Process the tree canopy cover data
logger.enable(meta = prj_meta, filename = "NLCD_tree_canopy_cover_processing.log", replace = True)
print("NLCD Tree Canopy Cover Processing Log\n")
nlcd.process_service_data("tree_canopy_cover")
print("\nNLCD Tree Canopy Cover processing completed. Check the log file for details.")
logger.disable()






# Define the metadata for the processed raster
print(f"- Defining metadata for {raster_name}...")
mdo = md.Metadata()
mdo.title = f"{cb_url[service_name]['name']} {year}"
mdo.tags = "Orange County, California, NLCD, Land Cover, Imagery"
mdo.summary = f"{cb_url[service_name]['name']} for Orange County, California for the year {year}. This raster was processed from the original ArcGIS Online Image Service by clipping it to the OC boundaries and extracting the relevant pixels. The original service URL is {service_url}."
mdo.description = f"{cb_url[service_name]['name']} for Orange County, California for the year {year}. This raster was processed from the original ArcGIS Online Image Service by clipping it to the OC boundaries and extracting the relevant pixels. The original service URL is {service_url}. Version: {nlcd.version}. Last updated: {nlcd.data_date}."
mdo.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdo.accessConstraints = """The feed data and associated resources (maps, apps, endpoints) can be used under a <a href=\"https://creativecommons.org/licenses/by-sa/3.0/\" target=\"_blank\">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. <div><br /></div><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless the data feed is provided, 'as is' and OC Public Work's standard <a href=\"https://www.ocgov.com/contact-county/disclaimer\" target=\"_blank\">Disclaimer</a> applies.</div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style=\"text-align:center;\"><a href=\"https://www.linkedin.com/in/ktalexan/\" target=\"_blank\"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style=\"text-align:center;\">GIS Analyst | Spatial Complex Systems Scientist</div><div style=\"text-align:center;\">OC Public Works/OC Survey Geospatial Applications</div><div style=\"text-align:center;\"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href=\"mailto:kostas.alexandridis@ocpw.ocgov.com\" target=\"_blank\">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div></div>"""
mdo.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/67ce28a349d14451a55d0415947c7af3/data"

# Save the metadata to the processed raster
print(f"- Saving metadata for {raster_name}...")
raster_md =md.Metadata(os.path.join(service_gdb, raster_name))
if not raster_md.isReadOnly:
    raster_md.copy(mdo)
    raster_md.save()




# Path to your ArcGIS Pro project
aprx = arcpy.mp.ArcGISProject(prj_dirs["gis_ocnlcd_aprx"])
gdb_path = prj_dirs["gis_ocnlcd_gdb"]
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

# ArcGIS Online Feature Service URL for the NLCD land cover data
nlcd_url = cb_url["land_cover"]["service"]

# ArcGIS Online Feature Service URL for the NLCD land cover change data
# nlcc_url = cb_url["land_cover_change"]["service"]


# Add the oc boundaries layer to the map from the supporting geodatabase
oc_lyr = m.addDataFromPath(os.path.join(prj_dirs["gis_supporting_gdb"], "oc_boundaries"))

nlcd_years = range(1985, 2025)

# years = range(2010, 2025)

for year in nlcd_years:
    print(f"Processing NLCD for year {year}...")
    where = f"Year = {year}"
    lyr = f"nlcd_{year}"

    arcpy.management.MakeImageServerLayer(
        nlcd_url,
        lyr,
        where_clause = where,
        mosaic_method = "ByAttribute"
    )

    arcpy.management.Clip(
        in_raster = lyr,
        out_raster = os.path.join(gdb_path, f"nlcd_{year}"),
        in_template_dataset = oc_lyr,
        nodata_value = "255",
        clipping_geometry = "NONE",
        maintain_clipping_extent="NO_MAINTAIN_EXTENT"
    )

    with arcpy.EnvManager(scratchWorkspace = gdb_path):
        out_raster = arcpy.sa.ExtractByMask(
            in_raster = os.path.join(gdb_path, f"nlcd_{year}"),
            in_mask_data=os.path.join(prj_dirs["gis_supporting_gdb"], "oc_boundaries"),
            extraction_area="INSIDE",
        )
        out_raster.save(os.path.join(gdb_path, f"ocnlcd_{year}"))

    # Delete intermediate raster
    arcpy.management.Delete(os.path.join(gdb_path, f"nlcd_{year}"))

# Save changes
aprx.save()
