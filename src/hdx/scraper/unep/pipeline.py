#!/usr/bin/python
"""UNEP scraper"""

import logging
import os
from os.path import join
from urllib.parse import urlencode

from arcgis.gis import GIS
from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.data.hdxobject import HDXError
from hdx.data.resource import Resource
from hdx.location.country import Country
from hdx.utilities.loader import load_json
from hdx.utilities.retriever import Retrieve
from hdx.utilities.saver import save_json
from html2text import html2text

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, configuration: Configuration, retriever: Retrieve, tempdir: str):
        self._configuration = configuration
        self._featureserver_url = configuration["featureserver_url"]
        self._download_url = configuration["download_url"]
        self._item_id = configuration["item_id"]
        self._retriever = retriever
        self._tempdir = tempdir
        self._last_temp_files = []
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

    def get_metadata(self) -> dict:
        """
        Get metadata including layers and countries
        """
        if self._retriever.use_saved:
            response = load_json(join(self._retriever.saved_dir, "gis_response.json"))
        else:
            gis = GIS()
            response = gis.content.get(self._item_id)
            if self._retriever.save:
                save_json(
                    response, join(self._retriever.saved_dir, "gis_response.json")
                )
        metadata = {}
        description = html2text(response["description"])
        metadata["description"] = description.replace("\n", " ").replace(
            "  ", "  \n  \n"
        )
        copyright = html2text(response["accessInformation"])
        copyright = copyright.replace("\n", " ").replace("  ", "")
        metadata["citation"] = f"**Citation:** {copyright}"
        countries = set()
        for layer_id in self._configuration["layer_id_to_type"]:
            layer_url = self._featureserver_url.format(layer_id=layer_id)
            countries.update(self.get_countries(layer_url))
        metadata["countries"] = [{"iso3": country} for country in sorted(countries)]
        return metadata

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
        end_year = attrs.get("end_Year")

        return start_year, end_year

    def generate_dataset(self, metadata: dict, countryiso: str) -> Dataset | None:
        """
        Get layer data from ArcGIS API and create data outputs for HDX
        Return dataset
        """
        # Dataset info
        countryname = Country.get_country_name_from_iso3(countryiso)
        dataset_name = f"unep_wdpca_{countryiso.lower()}"
        title = f"Protected and Conserved Areas (WDPCA) in {countryname}"
        dataset = Dataset(
            {
                "name": dataset_name,
                "title": title,
                "notes": metadata["description"],
                "caveats": metadata["citation"],
            }
        )
        try:
            dataset.add_country_location(countryiso)
        except HDXError:
            logger.error(f"Couldn't find country {countryiso}, skipping")
            return None
        base_filename = self._configuration["base_filename"]
        start_years = []
        end_years = []
        resources = []
        for layer_id, layer_type in self._configuration["layer_id_to_type"].items():
            layer_url = self._featureserver_url.format(layer_id=layer_id)
            start_year, end_year = self.get_date_range(layer_url, countryiso)
            if not start_year:
                continue
            start_years.append(start_year)
            end_years.append(end_year)
            for file_format, info in self._configuration["file_formats"].items():
                if file_format == "geoservice":
                    name = info["name"].format(layer_type=layer_type)
                    download_url = self._featureserver_url.format(layer_id=layer_id)
                else:
                    name = f"{base_filename}_{layer_type}.{info['file_ext']}"
                    download_url = self._download_url.format(
                        file_format=file_format, iso3=countryiso, layer_id=layer_id
                    )
                    if file_format != "csv":
                        download_url = f"{download_url}&spatialRefId=4326"
                resource = Resource(
                    {
                        "name": name,
                        "description": info["description"].format(
                            layer_type=layer_type
                        ),
                        "url": download_url,
                    }
                )
                resource.set_format(info.get("format", info.get("file_ext")))
                resources.append(resource)

        if len(start_years) == 0:
            logger.error(f"No data for {countryiso}, skipping")
            return None

        dataset.add_update_resources(resources)
        dataset.set_time_period_year_range(min(start_years), max(end_years))
        dataset.add_tags(self._configuration["tags"])
        dataset.set_subnational(True)

        return dataset
