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
                metadata = pipeline.get_metadata()
                assert len(metadata["countries"]) == 243
                dataset = pipeline.generate_dataset(metadata, "BOL")
                dataset.update_from_yaml(
                    path=join(config_dir, "hdx_dataset_static.yaml")
                )
                assert dataset == {
                    "name": "unep_wdpca_bol",
                    "title": "Protected and Conserved Areas (WDPCA) in Bolivia (Plurinational State of)",
                    "notes": "The WDPCA is the most comprehensive global database of marine and terrestrial protected areas and other effective area-based conservation measures. It is updated on a monthly basis and is one of the key global biodiversity datasets widely used by scientists, businesses, governments, international secretariats, and others to inform planning, policy decisions, and management.  \n  \nThe WDPCA is part of the Protected Planet Initiative, a joint product of the UN Environment Programme and the International Union for Conservation of Nature (IUCN). The compilation and management of the WDPCA is carried out by the UN Environment Programme World Conservation Monitoring Centre (UNEP-WCMC), in collaboration with governments and other stakeholders. Data and information on the world’s protected and conserved areas compiled in the WDPCA are used for reporting on progress towards Target 3 of the Kunming-Montreal Global Biodiversity Framework, which calls for 30% of the world’s land and waters to be effectively conserved by 2030. Additionally, the WDPCA is used for reporting to the United Nations to track progress towards the 2030 Sustainable Development Goals, the tracking of core indicators of the Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services (IPBES), and for providing information for other international assessments and reports including the Global Biodiversity Outlook. UNEP-WCMC and IUCN periodically release the Protected Planet Report on the status of the world’s protected and conserved areas.  \n  \nMany platforms incorporate the WDPCA to provide integrated information to diverse users, including businesses and governments across a range of sectors. For example, the WDPCA is included in the Integrated Biodiversity Assessment Tool (IBAT), an innovative decision-support tool that gives commercial users easy access to up-to-date information that allows them to identify biodiversity risks and opportunities within a project boundary. The reach of the WDPCA is further enhanced by the UN Biodiversity Lab, as well as services developed by other organisations such as Global Forest Watch and the Digital Observatory for Protected Areas. These platforms provide decision-makers with access to monitoring and alert systems that allow whole landscapes to be managed more effectively. Together, these applications of the WDPCA demonstrate the growing value and significance of the Protected Planet initiative.  \n  \n",
                    "caveats": "**Citation:** Protected Planet: The World Database on Protected Areas (WDPA)/The World Database on Other Effective Area-based Conservation Measures (WD-OECM) [On- line], [August 2026], Cambridge, UK: UNEP-WCMC and IUCN. Available at: https://doi.org/10.34892/6fwd-af11",
                    "groups": [{"name": "bol"}],
                    "dataset_date": "[1939-01-01T00:00:00 TO 2013-12-31T23:59:59]",
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
                    "subnational": "1",
                    "dataset_preview": "resource_id",
                    "license_id": "hdx-other",
                    "license_other": "[UNEP-WCMC WDPCA licence information](https://www.unep-wcmc.org/en/wdpa-data-license)",
                    "methodology": "Other",
                    "methodology_other": "The WDPCA is a joint project between UN Environment Programme and the International Union for Conservation of Nature (IUCN). The compilation and management of the WDPCA is carried out by UN Environment Programme World Conservation Monitoring Centre (UNEP-WCMC), in collaboration with governments, non-governmental organisations, academia and industry. More on methodology can be found [here](https://www.protectedplanet.net/en/thematic-areas/WDPCA?tab=Methodology).\n",
                    "dataset_source": "UNEP-WCMC, IUCN",
                    "package_creator": "HDX Data Systems Team",
                    "private": False,
                    "maintainer": "196196be-6037-4488-8b71-d786adf4c081",
                    "owner_org": "ca802a27-cc96-4c7b-aab2-a494a0fa64c9",
                    "data_update_frequency": 30,
                }
                assert dataset.get_resources() == [
                    {
                        "name": "protected_conserved_areas_WDPCA_points.gpkg",
                        "description": "GeoPackage format of the summary of points",
                        "url": "https://hub.arcgis.com/api/download/v1/items/8664a0d82205448e942c1189775846be/geopackage?layers=0&where=ISO3+%3D+%27BOL%27&redirect=true&spatialRefId=4326",
                        "format": "geopackage",
                        "dataset_preview_enabled": "False",
                    },
                    {
                        "name": "protected_conserved_areas_WDPCA_points.geojson",
                        "description": "GeoJSON format of the summary of points",
                        "url": "https://hub.arcgis.com/api/download/v1/items/8664a0d82205448e942c1189775846be/geojson?layers=0&where=ISO3+%3D+%27BOL%27&redirect=true&spatialRefId=4326",
                        "format": "geojson",
                        "dataset_preview_enabled": "True",
                    },
                    {
                        "name": "protected_conserved_areas_WDPCA_points.csv",
                        "description": "CSV format of the summary of points",
                        "url": "https://hub.arcgis.com/api/download/v1/items/8664a0d82205448e942c1189775846be/csv?layers=0&where=ISO3+%3D+%27BOL%27&redirect=true",
                        "format": "csv",
                        "dataset_preview_enabled": "False",
                    },
                    {
                        "name": "points GeoService",
                        "description": "ArcGIS Map Service of the summary of points",
                        "url": "https://services5.arcgis.com/Mj0hjvkNtV7NRhA7/arcgis/rest/services/WDPCA_v5/FeatureServer/0",
                        "format": "geoservice",
                        "dataset_preview_enabled": "False",
                    },
                    {
                        "name": "protected_conserved_areas_WDPCA_polygons.gpkg",
                        "description": "GeoPackage format of the summary of polygons",
                        "url": "https://hub.arcgis.com/api/download/v1/items/8664a0d82205448e942c1189775846be/geopackage?layers=1&where=ISO3+%3D+%27BOL%27&redirect=true&spatialRefId=4326",
                        "format": "geopackage",
                        "dataset_preview_enabled": "False",
                    },
                    {
                        "name": "protected_conserved_areas_WDPCA_polygons.geojson",
                        "description": "GeoJSON format of the summary of polygons",
                        "url": "https://hub.arcgis.com/api/download/v1/items/8664a0d82205448e942c1189775846be/geojson?layers=1&where=ISO3+%3D+%27BOL%27&redirect=true&spatialRefId=4326",
                        "format": "geojson",
                        "dataset_preview_enabled": "True",
                    },
                    {
                        "name": "protected_conserved_areas_WDPCA_polygons.csv",
                        "description": "CSV format of the summary of polygons",
                        "url": "https://hub.arcgis.com/api/download/v1/items/8664a0d82205448e942c1189775846be/csv?layers=1&where=ISO3+%3D+%27BOL%27&redirect=true",
                        "format": "csv",
                        "dataset_preview_enabled": "False",
                    },
                    {
                        "name": "polygons GeoService",
                        "description": "ArcGIS Map Service of the summary of polygons",
                        "url": "https://services5.arcgis.com/Mj0hjvkNtV7NRhA7/arcgis/rest/services/WDPCA_v5/FeatureServer/1",
                        "format": "geoservice",
                        "dataset_preview_enabled": "False",
                    },
                ]
