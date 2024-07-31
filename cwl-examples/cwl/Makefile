
build:
	docker build -t water-body-detection:local .

run:
	docker run -it -v ${PWD}:/runs water-body-detection:local python3 /app/app.py \
	--input-item https://earth-search.aws.element84.com/v0/collections/sentinel-s2-l2a-cogs/items/S2B_10TFK_20210713_0_L2A \
	--aoi "-121.399,39.834,-120.74,40.472" \
	--band green \
	--band nir \
	--epsg "EPSG:4326"

run-cwl:
	cwltool water-body-detect.cwl \
	--item "https://earth-search.aws.element84.com/v0/collections/sentinel-s2-l2a-cogs/items/S2B_10TFK_20210713_0_L2A" \
	--aoi="-121.399,39.834,-120.74,40.472" \
	--epsg "EPSG:4326" \
	--band "green" \
	--band "nir"
