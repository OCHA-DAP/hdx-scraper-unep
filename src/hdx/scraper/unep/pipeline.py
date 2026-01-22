#!/usr/bin/python
"""Unep scraper"""

import logging
import os
from os.path import basename, join
from pathlib import Path
from urllib.parse import urlencode

from geopandas import read_file
from geopandas.geodataframe import GeoDataFrame
from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.data.hdxobject import HDXError
from hdx.data.resource import Resource
from hdx.location.country import Country
from hdx.utilities.retriever import Retrieve

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, configuration: Configuration, retriever: Retrieve, tempdir: str):
        self._configuration = configuration
        self._url = configuration["url"]
        self._retriever = retriever
        self._tempdir = tempdir
        os.environ["OGR_ORGANIZE_POLYGONS"] = "SKIP"

    def get_countries(self, layer_url: str) -> set:
        query = {
            "f": "json",
            "returnGeometry": False,
            "returnDistinctValues": True,
            "outFields": "ISO3",
            "where": "ISO3 LIKE '___'",
        }
        response = self._retriever.download_json(
            f"{layer_url}/query?{urlencode(query)}"
        )
        return {x["attributes"]["iso3"] for x in response["features"]}

    def get_layersinfo(self) -> tuple[dict, list]:
        """
        Get layers
        """
        response = self._retriever.download_json(f"{self._url}?f=json")

        layers = response.get("layers", [])
        if not layers:
            return {}, []
        layer_id_to_type = {}
        countries = set()
        for layer in layers:
            if layer["type"] != "Feature Layer":
                continue
            layer_id = layer["id"]
            geometry_type = layer["geometryType"]
            if "point" in geometry_type:
                layer_type = "points"
            else:
                layer_type = "polygons"

            layer_id_to_type[layer_id] = layer_type
            countries.update(self.get_countries(f"{self._url}/{layer_id}"))
        return layer_id_to_type, [{"iso3": country} for country in sorted(countries)]

    def get_date_range(self, layer_url: str, countryiso: str) -> tuple[int, int]:
        """
        Get min & max dates using outStatistics from ArcGIS API
        """
        date_field = "STATUS_YR"  # date column from API
        stats = [
            {
                "statisticType": "min",
                "onStatisticField": date_field,
                "outStatisticFieldName": "start_year",
            },
            {
                "statisticType": "max",
                "onStatisticField": date_field,
                "outStatisticFieldName": "end_Year",
            },
        ]

        stats_query = {
            "f": "json",
            "outFields": "*",
            "outStatistics": stats,
            "returnGeometry": "false",
            "where": f"STATUS_YR > 0 AND ISO3='{countryiso}'",
        }
        stats_response = self._retriever.download_json(
            f"{layer_url}/query?{urlencode(stats_query)}"
        )

        attrs = stats_response["features"][0]["attributes"]
        start_year = attrs.get("start_year")
        end_year = attrs.get("end_year")

        return start_year, end_year

    def generate_geojson(
        self, gdf: GeoDataFrame, base_filename: str, layer_type: str
    ) -> Resource:
        filename = f"{base_filename}_{layer_type}.geojson"
        geojson_resource = Resource(
            {
                "name": filename,
                "description": f"GeoJSON format of the summary of {layer_type}",
            }
        )
        geojson_resource.set_format("geojson")
        filepath = join(self._tempdir, filename)
        gdf.to_file(filepath, driver="GeoJSON")
        geojson_resource.set_file_to_upload(filepath)
        return geojson_resource

    def generate_csv(
        self, gdf: GeoDataFrame, base_filename: str, layer_type: str
    ) -> Resource:
        filename = f"{base_filename}_{layer_type}.csv"
        csv_resource = Resource(
            {
                "name": filename,
                "description": f"CSV format of the summary of {layer_type}",
            }
        )
        csv_resource.set_format("csv")
        filepath = join(self._tempdir, filename)
        df_attributes = gdf.drop(columns="geometry")
        df_attributes.to_csv(filepath, index=False)
        csv_resource.set_file_to_upload(filepath)
        return csv_resource

    def generate_gpkg(self, gpkg_filepath: str) -> Resource:
        gpkg_resource = Resource(
            {
                "name": basename(gpkg_filepath),
                "description": "GPKG of point and polygon data",
            }
        )
        gpkg_resource.set_format("gpkg")
        gpkg_resource.set_file_to_upload(gpkg_filepath)
        return gpkg_resource

    def generate_geoservice(self, layer_url: str, layer_type: str) -> Resource:
        geoservice_resource = {
            "name": f"{layer_type} GeoService",
            "description": f"ArcGIS Map Service of the summary of {layer_type}",
            "url": layer_url,
            "format": "GeoService",
        }
        return Resource(geoservice_resource)

    def generate_dataset(
        self, layer_id_to_type: dict, countryiso: str
    ) -> Dataset | None:
        """
        Get layer data from ArcGIS API and create data outputs for HDX
        Return dataset
        """
        # Dataset info
        countryname = Country.get_country_name_from_iso3(countryiso)
        dataset_name = f"unep_wdpca_{countryiso.lower()}"
        title = f"Protected and Conserved Areas (WDPCA) in {countryname}"
        dataset = Dataset({"name": dataset_name, "title": title})
        try:
            dataset.add_country_location(countryiso)
        except HDXError:
            logger.error(f"Couldn't find country {countryiso}, skipping")
            return None
        base_filename = self._configuration["base_filename"]
        gpkg_filepath = join(self._tempdir, f"{base_filename}.gpkg")
        Path(gpkg_filepath).unlink(missing_ok=True)
        start_years = []
        end_years = []
        resources = []
        for layer_id, layer_type in layer_id_to_type.items():
            layer_url = f"{self._url}/{layer_id}"
            start_year, end_year = self.get_date_range(layer_url, countryiso)
            if not start_year:
                continue
            start_years.append(start_year)
            end_years.append(end_year)
            query = {
                "f": "json",
                "orderByFields": "OBJECTID",
                "outFields": "*",
                "geometryPrecision": 10,
                "maxAllowableOffset": 10,
                "where": f"ISO3='{countryiso}'",
            }
            query_url = f"{layer_url}/query?{urlencode(query)}"
            logger.info(f"Querying {query_url}")
            if self._retriever.save or self._retriever.use_saved:
                query_url = str(self._retriever.download_file(query_url))
            gdf = read_file("ESRIJSON:" + query_url)
            logger.info(f"Adding GPKG data for {layer_type}")
            gdf.to_file(gpkg_filepath, layer=layer_type, driver="GPKG")
            logger.info(f"Adding GeoJSON data for {layer_type}")
            resources.append(self.generate_geojson(gdf, base_filename, layer_type))
            logger.info(f"Adding csv data for {layer_type}")
            resources.append(self.generate_csv(gdf, base_filename, layer_type))
            logger.info(f"Adding GeoService for {layer_type}")
            resources.append(self.generate_geoservice(layer_url, layer_type))

        if len(start_years) == 0:
            logger.error(f"No data for {countryiso}, skipping")
            return None

        resources.insert(0, self.generate_gpkg(gpkg_filepath))
        dataset.preview_off()
        for resource in reversed(resources):
            if resource.get_format() == "geojson":
                resource.enable_dataset_preview()
                dataset.preview_resource()
                break
        dataset.add_update_resources(resources)
        start_years = sorted(start_years)
        end_years = sorted(end_years)
        dataset.set_time_period_year_range(start_years[0], end_years[-1])
        dataset.add_tags(self._configuration["tags"])

        return dataset
