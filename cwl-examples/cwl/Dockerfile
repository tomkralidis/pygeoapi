FROM docker.io/python:3.10-slim

RUN pip install --no-cache-dir \
    rasterio \
    click \
    pystac \
    loguru \
    pyproj \
    shapely \
    scikit-image \
    pystac \
    rio_stac && \
    python -c "import rasterio"

ADD app.py /app/app.py

ENTRYPOINT []
