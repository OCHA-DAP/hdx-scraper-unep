from os.path import join

from hdx.utilities.downloader import Download
from hdx.utilities.path import temp_dir
from hdx.utilities.retriever import Retrieve

from hdx.scraper.unep.pipeline import Pipeline


class TestPipeline:
    def test_pipeline(self, configuration, fixtures_dir, input_dir, config_dir):
        with temp_dir(
            "TestUNEP",
            delete_on_success=True,
            delete_on_failure=False,
        ) as tempdir:
            with Download(user_agent="test") as downloader:
                retriever = Retrieve(
                    downloader=downloader,
                    fallback_dir=tempdir,
                    saved_dir=input_dir,
                    temp_dir=tempdir,
                    save=False,
                    use_saved=True,
                )
                pipeline = Pipeline(configuration, retriever, tempdir)
                layer_id_to_type, countries = pipeline.get_layersinfo()
                assert len(layer_id_to_type) == 2
                assert len(countries) == 243
                dataset = pipeline.generate_dataset(layer_id_to_type, "BOL")
                dataset.update_from_yaml(
                    path=join(config_dir, "hdx_dataset_static.yaml")
                )
                assert dataset == {
                    "caveats": None,
                    "data_update_frequency": 30,
                    "dataset_date": "[1939-01-01T00:00:00 TO 2013-12-31T23:59:59]",
                    "dataset_preview": "resource_id",
                    "dataset_source": "UNEP",
                    "groups": [{"name": "bol"}],
                    "license_id": "cc-by-igo",
                    "maintainer": "196196be-6037-4488-8b71-d786adf4c081",
                    "methodology": "Other",
                    "methodology_other": "The WDPCA is a joint project between UN Environment "
                    "Programme and the International Union for Conservation "
                    "of Nature (IUCN). The compilation and management of the "
                    "WDPCA is carried out by UN Environment Programme World "
                    "Conservation Monitoring Centre (UNEP-WCMC), in "
                    "collaboration with governments, non-governmental "
                    "organisations, academia and industry. More on "
                    "methodology can be found "
                    "[here](https://www.protectedplanet.net/en/thematic-areas/WDPCA?tab=Methodology).\n",
                    "name": "unep_WDPCA_bol",
                    "notes": "The World Database on Protected and Conserved Areas (WDPCA) is the "
                    "most comprehensive global database of marine and terrestrial "
                    "protected areas. It is a joint project between UN Environment "
                    "Programme and the International Union for Conservation of Nature "
                    "(IUCN), and is managed by UN Environment Programme World "
                    "Conservation Monitoring Centre (UNEP-WCMC), in collaboration with "
                    "governments, non-governmental organisations, academia and "
                    "industry.\n",
                    "owner_org": "ca802a27-cc96-4c7b-aab2-a494a0fa64c9",
                    "package_creator": "HDX Data Systems Team",
                    "private": False,
                    "tags": [
                        {
                            "name": "environment",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        },
                        {
                            "name": "geodata",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        },
                    ],
                    "title": "Protected and Conserved Areas (WDPCA) in Bolivia (Plurinational "
                    "State of)",
                }
                assert dataset.get_resources() == [
                    {
                        "description": "GPKG of point and polygon data",
                        "format": "geopackage",
                        "name": "protected_conserved_areas_WDPCA.gpkg",
                    },
                    {
                        "description": "GeoJSON format of the summary of points",
                        "format": "geojson",
                        "name": "protected_conserved_areas_WDPCA_points.geojson",
                    },
                    {
                        "description": "CSV format of the summary of points",
                        "format": "csv",
                        "name": "protected_conserved_areas_WDPCA_points.csv",
                    },
                    {
                        "description": "ArcGIS Map Service of the summary of points",
                        "format": "GeoService",
                        "name": "points GeoService",
                        "url": "https://data-gis.unep-wcmc.org/server/rest/services/ProtectedPlanet/WDPCA/FeatureServer/0",
                    },
                    {
                        "dataset_preview_enabled": "True",
                        "description": "GeoJSON format of the summary of polygons",
                        "format": "geojson",
                        "name": "protected_conserved_areas_WDPCA_polygons.geojson",
                    },
                    {
                        "description": "CSV format of the summary of polygons",
                        "format": "csv",
                        "name": "protected_conserved_areas_WDPCA_polygons.csv",
                    },
                    {
                        "description": "ArcGIS Map Service of the summary of polygons",
                        "format": "GeoService",
                        "name": "polygons GeoService",
                        "url": "https://data-gis.unep-wcmc.org/server/rest/services/ProtectedPlanet/WDPCA/FeatureServer/1",
                    },
                ]
