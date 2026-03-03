# -*- coding: utf-8 -*-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Project: Orange County Land Cover/Land Use Data (OCLC)
# Title: OCLC Project Template Main Class ----
# Author: Dr. Kostas Alexandridis, GISP
# Date: March 2026
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import necessary libraries ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os
import sys
import datetime
from pathlib import Path
import json
import re
import logging
import unicodedata
from typing import List, Union, Optional, Dict, Any
import wmi
import pytz
import pandas as pd
import requests
import arcpy
from arcpy import metadata as md
from arcgis.features import GeoAccessor, GeoSeriesAccessor


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Dual Output: Define the class for logging ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class DualOutput:
    """
    A class to duplicate console output to a log file.
    """
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## DualOutput fx: Class initialization ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, filename: Optional[str] = None, meta: Optional[dict] = None):
        self._orig = None
        self._log = None
        self._filename = filename
        self._start_time = None
        self._end_time = None
        self._duration = None
        self._filetype = "log"  # Default filetype
        # Store optional project metadata so other methods can access it
        self.meta: Optional[dict] = meta
        self.project_name: Optional[str] = meta.get("name") if meta else None
        self.project_title: Optional[str] = meta.get("title") if meta else None
        self.project_version: Optional[float] = meta.get("version") if meta else None
        self.project_author: Optional[str] = meta.get("author") if meta else None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## DualOutput fx: Open log file ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _open_log(self, meta: dict, filename: str):
        # From the filename, determine if it's a .log, .txt, or .md file
        if filename.endswith(".md"):
            self._filetype = "markdown"
        elif filename.endswith(".log") or filename.endswith(".txt"):
            self._filetype = "log"
        if meta is not None:
            self.project_name = meta.get("name")
            self.project_title = meta.get("title")
            self.project_version = meta.get("version")
            self.project_author = meta.get("author")
        # Open the log file in append mode in the tests directory
        path = os.path.join(os.getcwd(), "logs", os.path.basename(filename))
        # Ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok = True)
        # If the file does not exist, open it and with an initial line
        if not os.path.isfile(path):
            with open(path, "w", encoding="utf-8") as f:
                # If it is a markdown file, write the header as the meta.get("project_name")
                if self._filetype == "markdown":
                    f.write(f"# {self.project_name}\n- Title: {self.project_title}\n- Version: {self.project_version}\n- Author: {self.project_author}\n- Filename: **{os.path.basename(filename)}**\n")
                elif self._filetype == "log":
                    # Write the project name and title in uppercase
                    f.write(f"Project Name: {self.project_name.upper()}\nProject Title: {self.project_title.upper()}\nVersion: {self.project_version}\nAuthor: {self.project_author}\nFilename: {os.path.basename(filename)}\n\n")
        # Return the opened file object
        return open(path, "a", encoding="utf-8")

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## DualOutput fx: Enable logging ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def enable(self, meta: Optional[dict] = None, filename: Optional[str] = None, replace: bool = False):
        log_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if self._orig is not None:
            return
        # Prefer provided meta, otherwise use stored meta
        if meta is not None:
            self.meta = meta
        # Determine the filetype based on the filename extension
        fn = filename or self._filename or "output.log"
        if fn.endswith(".md"):
            self._filetype = "markdown"
        elif fn.endswith(".log"):
            self._filetype = "log"
        elif fn.endswith(".txt"):
            self._filetype = "text"
        else:
            print("Warning: Unrecognized file extension. Defaulting to .log")
            self._filetype = "log"  # Default to log if no extension provided
            # Change filename to have .log extension
            fn = os.path.splitext(fn)[0] + ".log"
        self._orig = sys.stdout

        # If replace is requested, remove any existing file before opening
        if replace:
            try:
                path_to_remove = os.path.join(os.getcwd(), "logs", os.path.basename(fn))
                if os.path.isfile(path_to_remove):
                    os.remove(path_to_remove)
            except OSError:
                # If we cannot remove the file, continue and let _open_log handle errors
                pass

        self._log = self._open_log(meta, fn)
        sys.stdout = self
        self._start_time = datetime.datetime.now()

        if self._filetype == "markdown":
            print("----\n")
            print(f"\n> [!NOTE]\n> - Log ID: {log_id}\n> - Date: {datetime.datetime.now().strftime('%B %d, %Y')}\n> - Logging started at {self._start_time.strftime('%m/%d/%Y %H:%M:%S')}\n")
        else:
            print(f"---- Start of log ID: {log_id} ----")
            print(f"Date: {datetime.datetime.now().strftime('%B %d, %Y')}")
            print(f"Logging started at {self._start_time.strftime('%m/%d/%Y %H:%M:%S')}\n\n")

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## DualOutput fx: Disable logging ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def disable(self):
        self._end_time = datetime.datetime.now()
        if self._filetype == "markdown":
            print(f"\n> [!NOTE]\n> - Logging ended at {self._end_time.strftime('%m/%d/%Y %H:%M:%S')}")
        else:
            print(f"\n\nLogging ended at {self._end_time.strftime('%m/%d/%Y %H:%M:%S')}")
        self._duration = self._end_time - self._start_time
        if self._duration.total_seconds() < 60:
            if self._filetype == "markdown":
                print(f"> - Elapsed Time: {self._duration.total_seconds():.0f} seconds\n")
                print("----\n")
            else:
                print(f"Elapsed Time: {self._duration.total_seconds():.0f} seconds")
                print("---- End of log ----\n")
        else:
            # Display time in days, hours, minutes and seconds
            days, remainder = divmod(self._duration.total_seconds(), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            # Only show non-zero values
            if days > 0:
                if self._filetype == "markdown":
                    print(f"> - Elapsed Time: {int(days)} days, {int(hours)} hours, {int(minutes)} minutes and {int(seconds)} seconds\n")
                    print("----\n")
                else:
                    print(f"Elapsed Time: {int(days)} days, {int(hours)} hours, {int(minutes)} minutes and {int(seconds)} seconds")
                    print("---- End of log ----\n")
            elif hours > 0:
                if self._filetype == "markdown":
                    print(f"> - Elapsed Time: {int(hours)} hours, {int(minutes)} minutes and {int(seconds)} seconds\n")
                    print("----\n")
                else:
                    print(f"Elapsed Time: {int(hours)} hours, {int(minutes)} minutes and {int(seconds)} seconds")
                    print("---- End of log ----\n")
            elif minutes > 0:
                if self._filetype == "markdown":
                    print(f"> - Elapsed Time: {int(minutes)} minutes and {int(seconds)} seconds\n")
                    print("----\n")
                else:
                    print(f"Elapsed Time: {int(minutes)} minutes and {int(seconds)} seconds")
                    print("---- End of log ----\n")
            else:
                if self._filetype == "markdown":
                    print(f"> - Elapsed Time: {int(seconds)} seconds\n")
                    print("----\n")
                else:
                    print(f"Elapsed Time: {int(seconds)} seconds")
                    print("---- End of log ----\n")
        
        if self._orig is None:
            return
        sys.stdout = self._orig
        try:
            if self._log:
                self._log.close()
        finally:
            self._orig = None
            self._log = None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## DualOutput fx: Context manager enter ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __enter__(self):
        # Use stored metadata when entering context if available
        self.enable(meta=self.meta, filename=self._filename)
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## DualOutput fx: Context manager exit ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __exit__(self, exc_type, exc, tb):
        self.disable()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## DualOutput fx: Write output ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def write(self, message):
        if self._orig:
            self._orig.write(message)
        if self._log:
            try:
                self._log.write(message)
            except (OSError, UnicodeEncodeError):
                # Ignore known I/O/encoding errors when writing to the log; allow other exceptions to propagate
                pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## DualOutput fx: Flush output ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def flush(self):
        if self._orig:
            self._orig.flush()
        if self._log:
            try:
                self._log.flush()
            except OSError:
                # Ignore known I/O errors when flushing the log; allow other exceptions to propagate
                pass


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OCLC: Define the Main Class ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class OCLC:
    """
    A class to initialize the Orange County Land Cover/Land Use Data (OCLC) main project structure.
    The ProjectDirs class provides methods to set up the project directories and metadata. It is called by other classes such as OCGD, OCACS, OCTL, OCDC, and OCCR to inherit common functionality.
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## OCLC fx: Initialize project structure ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, part: int = 0, version: float = float(datetime.datetime.now().year)):
        """
        Initialize the OCLC class with the project structure.
        Args:
            Nothing
        Returns:
            Nothing
        Raises:
            Nothing
        Example:
            >>> oclc_init = OCLC()
        Notes:
            This function initializes the OCLC class with the project structure.
        """
        # Create a DualOutput instance for logging
        self.logger = DualOutput()

        # Set the part and version
        self.part = part
        self.version = version

        # Set the base path and data date
        self.base_path = os.getcwd()
        self.data_date = datetime.datetime.now().strftime("%B %Y")

        # Create a prj_dirs variable calling the project_directories function
        self.prj_dirs = self.project_directories(silent = False)

        # Attach project directories to logger so it's available to all logger methods
        try:
            self.logger.meta = self.prj_dirs
        except AttributeError:
            # Logger does not support 'meta' attribute; ignore safely
            pass

        # Set the Spatial Reference to Web Mercator
        self.sr = arcpy.SpatialReference(3857)  # Web Mercator


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## OCLC fx: Project directories ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def project_directories(self, silent: bool = False) -> dict:
        """
        Function to generate project directories for the OCLC data processing project.
        Args:
            silent (bool, optional): Whether to print the project directories. Defaults to False.
        Returns:
            directories (dict): A dictionary containing the project directories.
        Raises:
            None
        Example:
            >>> prj_dirs = project_directories("/path/to/project")
        Notes:
            The project_directories function is used to generate project directories for the OCLC data processing project.
        """
        # Define the project directories
        directories = {
            "root": self.base_path,
            "admin": os.path.join(self.base_path, "admin"),
            "analysis": os.path.join(self.base_path, "analysis"),
            "codebook": os.path.join(self.base_path, "codebook"),
            "data": os.path.join(self.base_path, "data"),
            "data_archived": os.path.join(self.base_path, "data", "archived"),
            "data_processed": os.path.join(self.base_path, "data", "processed"),
            "data_raw": os.path.join(self.base_path, "data", "raw"),
            "documentation": os.path.join(self.base_path, "documentation"),
            "gis": os.path.join(self.base_path, "gis"),
            "gis_archived": os.path.join(self.base_path, "gis", "archived"),
            "gis_layers": os.path.join(self.base_path, "gis", "layers"),
            "gis_layers_templates": os.path.join(self.base_path, "gis", "layers", "templates"),
            "gis_layouts": os.path.join(self.base_path, "gis", "layouts"),
            "gis_maps": os.path.join(self.base_path, "gis", "maps"),
            "gis_styles": os.path.join(self.base_path, "gis", "styles"),
            "gis_ochls": os.path.join(self.base_path, "gis", "ochls"),
            "gis_ochls_aprx": os.path.join(self.base_path, "gis", "ochls", "ochls.aprx"),
            "gis_ochls_gdb": os.path.join(self.base_path, "gis", "ochls", "ochls.gdb"),
            "gis_ocnlcd": os.path.join(self.base_path, "gis", "ocnlcd"),
            "gis_ocnlcd_aprx": os.path.join(self.base_path, "gis", "ocnlcd", "ocnlcd.aprx"),
            "gis_ocnlcd_gdb": os.path.join(self.base_path, "gis", "ocnlcd", "ocnlcd.gdb"),
            "gis_supporting_gdb": os.path.join(self.base_path, "gis", "supporting.gdb"),
            "graphics": os.path.join(self.base_path, "graphics"),
            "logs": os.path.join(self.base_path, "logs"),
            "metadata": os.path.join(self.base_path, "metadata"),
            "metadata_archived": os.path.join(self.base_path, "metadata", "archived"),
            "notebooks": os.path.join(self.base_path, "notebooks"),
            "notebooks_archived": os.path.join(self.base_path, "notebooks", "archived"),
            "scripts": os.path.join(self.base_path, "scripts"),
            "scripts_archived": os.path.join(self.base_path, "scripts", "archived"),
            "tests": os.path.join(self.base_path, "tests")
        }

        # Print the project directories
        if not silent:
            print("Project Directories:")
            for key, value in directories.items():
                print(f"- {key}: {value}")

        # Return the project directories
        return directories


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## OCLC fx: Load ArcGIS Pro Project ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def load_aprx(self, aprx_path: str, gdb_path: str, add_to_map: bool = False) -> tuple:
        """
        Loads an ArcGIS Pro project and sets the workspace to the geodatabase.
        Args:
            aprx_path (str): Path to the ArcGIS Pro project.
            gdb_path (str): Path to the geodatabase.
            add_to_map (bool): Whether to add outputs to the map.
        Raises:
            FileNotFoundError: If the ArcGIS Pro project or geodatabase does not exist.
            ValueError: If the ArcGIS Pro project or geodatabase path is invalid.
        Examples:
            >>> aprx, workspace = load_aprx(aprx_path, gdb_path, add_to_map=True)
        Returns:
            tuple: A tuple containing the ArcGIS Pro project object and the workspace.
        Notes:
            - The ArcGIS Pro project will be closed before loading.
            - The workspace will be set to the geodatabase path.
            - The ArcGIS Pro project will be closed after loading.
        """
        # ArcGIS Pro Project object
        aprx = arcpy.mp.ArcGISProject(aprx_path)
        # Current ArcGIS workspace (arcpy)
        arcpy.env.workspace = gdb_path
        workspace = arcpy.env.workspace
        # Enable overwriting existing outputs
        arcpy.env.overwriteOutput = True
        # Disable adding outputs to map
        arcpy.env.addOutputsToMap = add_to_map
        return aprx, workspace


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OCHLS: Define the main class ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class OCHLS(OCLC):
    """Class Containing the Orange County Harmonized Landsat Sentinel v2 (OCHLS) Processing Workflow Functions.

    This class encapsulates the workflow for processing Orange County Harmonized Landsat Sentinel v2 (OCHLS)
    data. It includes methods for initialization, main execution, and retrieving
    metadata for various feature classes.
    """
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## OCHLS fx: Class initialization ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, part: int = 0, version: float = float(datetime.datetime.now().year)):
        """
        Initialize the OCHLS class.
        """
        # Initialize the OCHLS class with provided part/version
        super().__init__(part, version)

        # Create a prj_meta variable calling the project_metadata function
        self.prj_meta = self.project_metadata(silent = False)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## OCHLS fx: Project metadata ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    def project_metadata(self, silent: bool = False) -> dict:
        """
        Function to generate project metadata for the OCHLS data processing object.
        Args:
            silent (bool): If True, suppresses the print output. Default is False.
        Returns:
            metadata (dict): A dictionary containing the project metadata. The dictionary includes: name, title, description, version, author, years, date_start, date_end, date_updated, and TIMS metadata.
        Raises:
            ValueError: If part is not an integer, or if version is not numeric.
        Example:
            >>> metadata = self.project_metadata()
        Notes:
            This function generates a dictionary with project metadata based on the provided part and version.
            The function also checks if the TIMS metadata file exists and raises an error if it does not.
        """
        
        # Match the part to a specific step and description (with default case)
        match self.part:
            case 0:
                step = "Part 0: General Data Updating"
                desc = "General Data Updating and Maintenance"
            case 1:
                step = "Part 1: Raw Data Processing"
                desc = "Processing Raw Tiger/Line TigerWeb REST API Services and Creating Geodatabases"
            case 2:
                step = "Part 2: Part 2: ArcGis Pro Project Map Processing"
                desc = "Initialize the ArcGIS Pro Project with Maps and Layers, and process map layers from the TL Geodatabases"
            case 3:
                step = "Part 3: Sharing and Publishing Feature Classes"
                desc = "Sharing and Publishing Feature Classes to ArcGIS Online"
            case _:
                step = "Part 0: General Data Updating"
                desc = "General Data Updating and Maintenance (default)"
        
        # Create a dictionary to hold the metadata
        metadata = {
            "name": "OCHLS v2 Data Processing",
            "title": step,
            "description": desc,
            "version": self.version,
            "date": self.data_date,
            "author": "Dr. Kostas Alexandridis, GISP",
            "years": "",
        }

        # If not silent, print the metadata
        if not silent:
            print(
                f"\nProject Metadata:\n- Name: {metadata['name']}\n- Title: {metadata['title']}\n- Description: {metadata['description']}\n- Version: {metadata['version']}\n- Author: {metadata['author']}"
            )
        
        # Return the metadata
        return metadata


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OCNLCD: Define the main class ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class OCNLCD(OCLC):
    """
    A class containing functions and methods for the Orange County National Land Cover Database (OCNLCD) Project.
    Attributes:
        None
    Methods:
        project_metadata(part: int, version: float = float(datetime.datetime.now().year), silent: bool = False) -> dict:
            Generates project metadata for the OCNLCD data processing project.
        project_directories(silent: bool = False) -> dict:
            Generates project directories for the OCNLCD data processing project.
    Returns:
        None
    Raises:
        None
    Examples:
        >>> metadata = project_metadata(1, 1)
        >>> prj_dirs = project_directories()
    Notes:
        This class is used to generate project metadata and directories for the OCNLCD project.
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## OCNLCD fx: Class initialization ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, part: int = 0, version: float = float(datetime.datetime.now().year)):
        """
        Initializes the OCNLCD class.
        """
        # Initialize the OCNLCD class with provided part/version
        super().__init__(part, version)

        # Create a prj_meta variable calling the project_metadata function
        self.prj_meta = self.project_metadata(silent = False)

        # Load the service codebook information into a variable for use in other methods
        self.cb_url = self.service_codebook()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## OCNLCD fx: Project metadata ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def project_metadata(self, silent: bool = False) -> dict:
        """
        Function to generate project metadata for the OCNLCD data processing project.
        Args:
            silent (bool, optional): Whether to print the metadata information. Defaults to False.
        Returns:
            prj_meta (dict): A dictionary containing the project metadata.
        Raises:
            ValueError: If part is not an integer, or if version is not numeric.
        Example:
            >>> metadata = project_metadata(1, 1)
        Notes:
            The project_metadata function is used to generate project metadata for the OCNLCD data processing project.
        """

        # Match the part to a specific step and description (with default case)
        match self.part:
            case 1:
                step = "Part 1: Raw Data Processing"
                desc = "Importing the raw data files and perform initial geocoding"
            case 2:
                step = "Part 2: Imported Data Geocoding"
                desc = "Geocoding the imported data and preparing it for GIS processing."
            case 3:
                step = "Part 3: GIS Data Processing"
                desc = "GIS Geoprocessing and formatting of the OCUP data."
            case 4:
                step = "Part 4: GIS Map Processing"
                desc = "Creating maps and visualizations of the OCUP data."
            case 5:
                step = "Part 5: GIS Data Sharing"
                desc = "Exporting and sharing the GIS data to ArcGIS Online."
            case _:
                step = "Part 0: General Data Processing"
                desc = "General data processing and analysis (default)."

        # Create a dictionary to hold the metadata
        metadata = {
            "name": "OCNLCD Data Processing",
            "title": step,
            "description": desc,
            "version": self.version,
            "date": self.data_date,
            "author": "Dr. Kostas Alexandridis, GISP",
            "years": "",
        }

        # If not silent, print the metadata
        if not silent:
            print(
                f"\nProject Metadata:\n- Name: {metadata['name']}\n- Title: {metadata['title']}\n- Description: {metadata['description']}\n- Version: {metadata['version']}\n- Author: {metadata['author']}"
            )

        # Return the metadata
        return metadata


    def service_codebook(self) -> dict:
        """
        Function to retrieve the codebook information for the OCNLCD data processing project.
        Args:
            None
        Returns:
            codebook (dict): A dictionary containing the codebook information.
        Raises:
            None
        Example:
            >>> codebook = service_codebook()
        Notes:
            The service_codebook function is used to retrieve the codebook information for the OCNLCD data processing project. The codebook information is stored in a JSON file in the codebook directory.
        """
        # Path to the codebook JSON file
        service_codebook_path = os.path.join(self.prj_dirs["codebook"], "cb_url.json")

        # Load the codebook information from the JSON file
        with open(service_codebook_path, "r", encoding = "utf-8") as f:
            codebook = json.load(f)

        return codebook


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## OCNLCD fx: Process service data ----
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def process_service_data(self, service_name: str):
        """
        Process the specified service data by clipping it to the OC boundaries and adding it to the ArcGIS Pro project.
        Args:
            service_name (str): The name of the service to process (e.g., "land_cover", "land_cover_change", etc.).
        Returns:
            None
        Raises:
            ValueError: If the service name is not found in the codebook.
        Example:
            >>> process_service_data("land_cover")
            Processing land_cover for year 1985...
        Note:
            This function assumes that the codebook (cb_url) contains the necessary information for the specified service, including the service URL, years to process, nodata value, and base layer name. It also assumes that the ArcGIS Pro project and supporting geodatabase are set up according to the project directories specified in prj_dirs.
        """

        # Check if the service name is in the codebook
        if service_name not in self.cb_url:
            print(f"Service name '{service_name}' not found in the codebook.")
            return None

        # Get the service URL and years from the codebook
        service_url = self.cb_url[service_name]["service"]
        service_years = self.cb_url[service_name]["years"]
        service_nodata = self.cb_url[service_name]["nodata value"]
        service_base_layer = self.cb_url[service_name]["base layer"]
        service_field = self.cb_url[service_name]["field"]

        # Path to the project ArcGIS Pro Project
        aprx = arcpy.mp.ArcGISProject(self.prj_dirs["gis_ocnlcd_aprx"])

        # Get the service geodatabase name from the codebook
        service_gdb = os.path.join(self.prj_dirs["gis_ocnlcd"], self.cb_url[service_name]["database"])

        # Set the ArcGIS Pro environment workspace to the service geodatabase
        arcpy.env.workspace = service_gdb
        arcpy.env.overwriteOutput = True

        # Delete all maps in the service geodatabase
        # print("Deleting existing maps in the service geodatabase...")
        # for m in aprx.listMaps():
        #     # If the map does not start with the service name, delete it
        #     if not m.name.startswith(service_name):
        #         print(f"Deleting map: {m.name}")
        #         aprx.deleteItem(m)

        # Create a new map for the service if it doesn't exist
        service_map = service_name + "_map"
        if service_map not in [m.name for m in aprx.listMaps()]:
            # Create a new map for the service
            m = aprx.createMap(service_map)
            m.addBasemap("Topographic")
        else:
            # Get the existing map for the service
            m = aprx.listMaps(service_map)[0]

        # Activate the map
        m.openView()
        print(f"Activating map: {m.name}")

        # Remove all the rasters from the map
        for lyr in m.listLayers():
            if lyr.isRasterLayer:
                m.removeLayer(lyr)
        
        # Delete all rasters from the geodatabase
        for raster in arcpy.ListRasters():
            arcpy.management.Delete(raster)

        # Add the oc boundaries layer to the map from the supporting geodatabase
        oc_lyr = m.addDataFromPath(os.path.join(self.prj_dirs["gis_supporting_gdb"], "oc_boundaries"))

        for year in service_years:
            print(f"\nProcessing {service_name} for year {year}...")
            where = f"{service_field} = {year}"
            lyr = f"temp_{year}"
            raster_name = f"{service_base_layer}_{year}"

            # Create a temporary layer from the ArcGIS Online Image Service for the specified year
            print(f"- Creating temporary layer for year {year}...")
            arcpy.management.MakeImageServerLayer(
                service_url,
                lyr,
                where_clause = where,
                mosaic_method = "ByAttribute"
            )

            # Clip the temporary layer to the OC boundaries and save it to the service geodatabase
            print(f"- Clipping layer to OC boundaries for year {year}...")
            arcpy.management.Clip(
                in_raster = lyr,
                out_raster = os.path.join(service_gdb, lyr),
                in_template_dataset = oc_lyr,
                nodata_value = service_nodata,
                clipping_geometry = "NONE",
                maintain_clipping_extent="NO_MAINTAIN_EXTENT"
            )

            # Extract the relevant pixels from the clipped raster and save it to the service geodatabase
            print(f"- Extracting relevant pixels for year {year}...")
            with arcpy.EnvManager(scratchWorkspace = service_gdb):
                out_raster = arcpy.sa.ExtractByMask(
                    in_raster = os.path.join(service_gdb, lyr),
                    in_mask_data=os.path.join(self.prj_dirs["gis_supporting_gdb"], "oc_boundaries"),
                    extraction_area="INSIDE",
                )
                out_raster.save(os.path.join(service_gdb, raster_name))

            # Delete intermediate raster
            print(f"- Deleting intermediate raster for year {year}...")
            arcpy.management.Delete(os.path.join(service_gdb, lyr))

            # Re-project the raster to match the project spatial reference
            print(f"- Re-projecting raster for year {year}...")
            arcpy.management.ProjectRaster(
                in_raster = os.path.join(service_gdb, raster_name),
                out_raster = os.path.join(service_gdb, raster_name),
                out_coor_system = self.sr
            )

        # Add the processed rasters to the map
        print("\nAdding processed rasters to the map...")
        for raster in arcpy.ListRasters():
            print(f"- Adding raster {raster} to the map...")
            # Add the raster to the map
            m.addDataFromPath(os.path.join(service_gdb, raster))

        # Close the map view
        aprx.closeViews("MAPS")

        # Save changes
        print("Saving changes to the project...")
        aprx.save()

        return None


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    pass


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# End of Script ----
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
