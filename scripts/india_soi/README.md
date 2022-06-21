## india_soi

This directory houses the source code to process the maps downloaded from the
Survey of India (SoI) portal.

> Please note that the maps are downloadable upon
purchase.

There are different maps that are available in the map bundle from SoI, and we
process the maps with the boundaries for state, district and subdistricts.


In order to run the script to generate geojson mcf files for state, district and
subdistrict boundaries of India, the following steps needs to be done.

1. Download and extract the shapefiles from Survey of India
2. Run the following command to generate geojson mcfs from the input shapefile

```bash
python3 process_soi_maps.py --geo=dist --input_path=<path to the shapefile>
--output_path=<path to the output directory> --simplify=True
```

#### Notes:
1. At present, the KG does not support the import of subdistricts, the
   `--geo=subdist` will throw a waring message that dcids are not resolved.
2. The shapefiles use the [Local Government Directory (LGD) codes](https://lgdirectory.gov.in/) for place
   resolution, and the script uses the same code for resolving places.
3. The disputed territories and missing LGD codes are added through the script
