# Brazil's South STAC-FABDEM

The FABDEM (Forest And Buildings removed Copernicus DEM) is a global elevation map, developed by the University of Bristol (Neal et al. 2023) that removes building and tree height biases from the Copernicus GLO 30 Digital Elevation Model (DEM), as described by Hawker et al. (2022). 

This dataset is a major improvement over traditional DEMs currently available through the cloud platforms Google Earth Engine or Microsoft Planetary. However there is a drawback. Although the data is originally provided in 1-deg tiles saved in COG (Cloud Optimized GeoTIFF) format, it is grouped in 10 by 10 degrees ZIP files that makes it cumbersome for "on-demand" retrieval.

With that in mind, the current repository demonstrates how to re-organize this data and re-publish it as a STAC dataset directly on GitHub. The processing has been performed for the South region of Brazil (image below).

![image](https://github.com/cordmaur/fabdem-brazil-south/assets/19617404/cf83dcd1-5012-40bc-8a15-fc6d5238f9a7)

## STAC-FABDEM creation
The whole procedure is described in the notebook `nbs/01-StacCreation-BrSouth.ipynb`. 

## Usage
The notebook `nbs/02-FABDEM_Usage.ipynb` describes the process, but in summary, it relies on 3 main components:
* STAC catalog: published in the `/stac_catalog folder`
* Search Function: This function selects the STAC items that intersects the region of interest. The code is available at `/nbs/utils.py`
* `STACKSTAC` library: library to stack STAC items into a DASK cube (https://github.com/gjoseph92/stackstac).
  
As this is not a full STAC server implementation, we are going to use `pystac` instead of the `pystac_client` library. 
Initially, we can load the STAC catalog directly from GitHub with the following commands:
```
import pystac 

catalog = pystac.Catalog.from_file(href='https://github.com/cordmaur/fabdem-brazil-south/raw/main/stac_catalog/catalog.json')
catalog
```
![image](https://github.com/cordmaur/fabdem-brazil-south/assets/19617404/3c18d301-84c6-4743-a763-50b6f98e616e)

Then, assuming we have a region of interest, we can search the STAC items that touches the region, by using the `search_catalog` function. 
```
from shapely.geometry import box
from utils import search_catalog

# Create an region of interest as a bounding box
bbox = box(-56.2, -30.8, -54.8, -30.2)

# select the items intersecting out area of interest (bbox)
items = search_catalog(catalog, bbox)
items
```
![image](https://github.com/cordmaur/fabdem-brazil-south/assets/19617404/7dc997ae-dc12-4e0a-b997-c3862c6b524d)
![image](https://github.com/cordmaur/fabdem-brazil-south/assets/19617404/651c4d05-8a78-4d7e-9d2b-bb0e7b4b75d8)

With the intersecting STAC items selected, we can retrieve the FABDEM for the desired ROI by calling `stackstac.stack` method, like so:
```
import stackstac

# create a cube with the items stacked
cube = stackstac.stack(
    items=items,
    bounds_latlon=bbox.bounds
)

# reduce the cube in the "time" dimension
dem = cube.mean(dim='time').squeeze().compute()

# plot the region
dem.plot.imshow(robust=True, aspect=1, vmin=50, vmax=200, figsize=(14, 5)) #type: ignore
```
![image](https://github.com/cordmaur/fabdem-brazil-south/assets/19617404/cfabb095-f1e5-423e-9844-0274fba39fc3)


# References
* Neal, J. (Creator), Hawker, L. (Creator), Uhe, P. (Contributor),
Paulo, L. (Contributor), Sosa, J. (Contributor), Savage, J. (Contributor),
Sampson, C. (Contributor) (17 Jan 2023). FABDEM V1-2. University of Bristol. 10.5523/bris.s5hqmjcdj8yo2ibzi9b4ew3sn

* Hawker, Laurence, Peter Uhe, Luntadila Paulo, Jeison Sosa, James Savage, Christopher Sampson, and Jeffrey Neal. “A 30 m Global Map of Elevation with Forests and Buildings Removed.” Environmental Research Letters 17, no. 2 (February 2022): 024016. https://doi.org/10.1088/1748-9326/ac4d4f.


