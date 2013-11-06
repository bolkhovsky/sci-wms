__author__ = 'ilya'

import sys, os
from django.http import HttpResponse
import mapscript
from pywms import server_local_config as config

def wms(request, dataset):
    ows = mapscript.OWSRequest()
    ows.setParameter("STYLES", "")
    ows.setParameter("LAYERS", "image")
    ows.setParameter("COVERAGE", "image")

    for key in ['request', 'version', 'transparency', 'service', 'srs', 'width', 'height', 'bbox', 'format']:
        if request.GET.has_key(key.upper()) and request.GET[key.upper()]:
            ows.setParameter(key.upper(), request.GET[key.upper()])

    mapsv = mapscript.mapObj(os.path.join(config.fullpath_to_wms, 'maps', 'wms.map'))
    mapsv.applyConfigOptions()

    raster = mapscript.layerObj(mapsv)
    raster.name = "image"
    raster.type = mapscript.MS_LAYER_RASTER
    raster.data = os.path.join(config.fullpath_to_wms, 'testdata', 'ASA_WSM_1PNPDE20110815_090644_000001903105_00309_49461_8731.N1_epsg3857.tif')
    raster.status = mapscript.MS_ON
    raster.dump = mapscript.MS_TRUE
    raster.debug = mapscript.MS_TRUE
    raster.metadata.set('wcs_formats', 'GEOTIFF')
    raster.metadata.set('wms_title', ("sci-wms service"))
    raster.metadata.set('wms_srs', 'EPSG:4326')
    #raster.offsite = mapscript.colorObj(255, 255, 255)

    mapscript.msIO_installStdoutToBuffer()
    result = mapsv.OWSDispatch(ows)

    if result == 2:
        raise Exception('no valid OWS request in the req object')
    elif result == 1:
        raise Exception('OWS request was not successfully processed')

    content_type = mapscript.msIO_stripStdoutBufferContentType() or "text/plain"
    result_data = mapscript.msIO_getStdoutBufferBytes()

    response = HttpResponse(content_type=content_type)
    response.write(result_data)
    mapscript.msIO_resetHandlers
    return response
