#!/bin/bash


kibana_url="localhost:5601"
elasticsearch_url="localhost:9200"
saved_objects="/home/tmr/Downloads/sast.json"

until curl -u elastic:changeme -s "$elasticsearch_url/_cluster/health?pretty" | grep '"status"' | grep -qE "green|yellow"; do
    curl -s "$elasticsearch_url/_cluster/health?pretty"
    echo "Waiting for Elasticsearch..."
    sleep 5
done


# Export a dashboard :
#curl -k -XGET 'http://localhost:5601/api/kibana/dashboards/export?dashboard=e0f75470-99b0-11e9-b21e-d3998332c496' -u elastic:changeme > appsecdash.json

# Import a dashboard :
# curl -u elastic:changeme -k -XPOST 'http://localhost:5601/api/kibana/dashboards/import' -H 'Content-Type: application/json' -H "kbn-xsrf: true" -d @appsecdash.json

