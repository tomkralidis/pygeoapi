
echo
curl -XDELETE http://localhost:9200/canada-surface-weather-obs
echo
curl -XPUT http://localhost:9200/canada-surface-weather-obs
echo
curl -XPOST http://localhost:9200/canada-surface-weather-obs/_doc  -H 'Content-Type: application/json' -d @test-data/2023-03-28-0143-CVOO-AUTO-minute-swob.xml.json 

echo
echo
echo "done"
echo
