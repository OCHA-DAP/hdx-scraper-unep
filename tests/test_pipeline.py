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
                metadata = pipeline.get_netadata()
                assert len(metadata["layer_id_to_type"]) == 2
                assert len(metadata["countries"]) == 243
                dataset = pipeline.generate_dataset(metadata, "BOL")
                dataset.update_from_yaml(
                    path=join(config_dir, "hdx_dataset_static.yaml")
                )
                assert dataset == {
                    "caveats": "**Citation:** UNEP-WCMC and IUCN (2026), Protected Planet: The "
                    "World Database on Protected and Conserved Areas (WDPCA) "
                    "[On-line], [January 2026], Cambridge, UK: UNEP-WCMC and IUCN. "
                    "Available at:\u202fhttps://doi.org/10.34892/NSDV-9P22",
                    "data_update_frequency": 30,
                    "dataset_date": "[1939-01-01T00:00:00 TO 2013-12-31T23:59:59]",
                    "dataset_preview": "resource_id",
                    "dataset_source": "UNEP-WCMC, IUCN",
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
                    "name": "unep_wdpca_bol",
                    "notes": "The\xa0World Database on Protected and Conserved Areas (WDPCA)\xa0"
                    "combines\xa0the\xa0formerly separate\xa0World Database on Protected "
                    "Areas (WDPA) and\xa0World Database on Other Effective Area-based "
                    "Conservation Measures (WD-OECM). The WDPCA is\xa0the most "
                    "comprehensive global database\xa0of marine and terrestrial "
                    "protected areas and other effective area-based conservation "
                    "measures, updated on a monthly basis, and\xa0is\xa0one of the key "
                    "global biodiversity datasets being widely used by scientists, "
                    "businesses, governments,\xa0international secretariats,\xa0and "
                    "others to inform planning, policy decisions,\xa0and management.\n"
                    "\n"
                    "The\xa0WDPCA is\xa0part of the Protected Planet Initiative,\xa0a "
                    "joint product of\xa0the\xa0UN Environment Programme and the "
                    "International Union for Conservation of Nature (IUCN). The "
                    "compilation and management of the\xa0WDPCA\xa0is carried out by\xa0"
                    "the\xa0UN Environment Programme World Conservation Monitoring "
                    "Centre (UNEP-WCMC), in collaboration with governments and other "
                    "stakeholders. Data and information on the world's protected\xa0and "
                    "conserved\xa0areas\xa0compiled in the\xa0WDPCA is\xa0used for "
                    "reporting on progress towards reaching\xa0Target 3 of\xa0the "
                    "Kunming-Montreal Global Biodiversity Framework, which calls for 30% "
                    "of the world’s land and waters to be effectively conserved by "
                    "2030.\n"
                    "\n"
                    "Additionally,\xa0the WDPCA is used\xa0for reporting\xa0to the UN to "
                    "track progress towards the 2030 Sustainable Development Goals,\xa0"
                    "tracking of\xa0core indicators\xa0of the Intergovernmental "
                    "Science-Policy Platform on Biodiversity and Ecosystem Services "
                    "(IPBES), and\xa0providing information for\xa0other international "
                    "assessments and reports including the Global Biodiversity Outlook. "
                    "UNEP-WCMC and IUCN periodically release the Protected Planet Report "
                    "on the status of the world's protected and conserved areas.\n"
                    "\n"
                    "Many platforms are incorporating the\xa0WDPCA\xa0to provide "
                    "integrated information to diverse users, including businesses and "
                    "governments, in a range of sectors. For example, the\xa0WDPCA\xa0"
                    "is\xa0included in the Integrated Biodiversity Assessment Tool\xa0"
                    "(IBAT), an innovative decision support tool that gives\xa0"
                    "commercial\xa0users easy access to up-to-date information that "
                    "allows them to\xa0identify\xa0biodiversity risks and opportunities "
                    "within a project boundary.\n"
                    "\n"
                    "The reach of the\xa0WDPCA is\xa0further enhanced\xa0by\xa0the UN "
                    "Biodiversity Lab as well as\xa0services\xa0developed by other "
                    "parties, such as the Global Forest Watch and the Digital "
                    "Observatory for Protected Areas, which provide decision makers with "
                    "access to monitoring and alert systems that allow whole landscapes "
                    "to be managed better. Together, these applications of the\xa0"
                    "WDPCA\xa0demonstrate the growing value and significance of the "
                    "Protected Planet initiative.",
                    "owner_org": "ca802a27-cc96-4c7b-aab2-a494a0fa64c9",
                    "package_creator": "HDX Data Systems Team",
                    "private": False,
                    "subnational": "1",
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
