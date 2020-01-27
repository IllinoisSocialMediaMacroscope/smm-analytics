#!/usr/bin/env bash
docker push socialmediamacroscope/classification_predict:latest
docker push socialmediamacroscope/classification_split:latest
docker push socialmediamacroscope/classification_train:latest
docker push socialmediamacroscope/histogram:latest
docker push socialmediamacroscope/network_analysis:latest
docker push socialmediamacroscope/preprocessing:latest
docker push socialmediamacroscope/sentiment_analysis:latest
docker push socialmediamacroscope/topic_modeling:latest
docker push socialmediamacroscope/name_entity_recognition:latest
docker push socialmediamacroscope/autophrase:latest
docker push socialmediamacroscope/clowder_create_collection:latest
docker push socialmediamacroscope/clowder_create_dataset:latest
docker push socialmediamacroscope/clowder_create_space:latest
docker push socialmediamacroscope/clowder_list:latest
docker push socialmediamacroscope/clowder_upload_file:latest
docker push socialmediamacroscope/crimson_hexagon_monitors:latest
docker push socialmediamacroscope/smile_server:latest
docker push socialmediamacroscope/smile_graphql:latest