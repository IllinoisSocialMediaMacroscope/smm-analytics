# set repository
docker_repo=socialmediamacroscope

# set build and push option
build=true
push=true

# set components selection
autophrase=true
biometer_check_bot=false
bulk_comparison=false
check_screen_name=false
classification_predict=false
classification_split=false
classification_train=false
clowder_create_collection=false
clowder_create_dataset=false
clowder_create_space=false
clowder_list=false
clowder_upload_file=false
collect_reddit_comment=false
collect_timeline=false
crimson_hexagon_monitors=false
get_personality=false
get_sim_score=false
histogram=false
image_crawler=false
name_entity_recognition=false
network_analysis=false
nginx=false
nginx_wo_ssl=false
preprocessing=false
screen_name_prompt=false
sentiment_analysis=false
topic_modeling=false
utku_brand_personality=false

# set version numbers
autophrase_version=PR-18
biometer_check_bot_version=1.0.0
bulk_comparison_version=1.0.0
check_screen_name_version=1.0.0
classification_predict_version=1.0.0
classification_split_version=1.0.0
classification_train_version=1.0.0
clowder_create_collection_version=1.0.0
clowder_create_dataset_version=1.0.0
clowder_create_space_version=1.0.0
clowder_list_version=1.0.0
clowder_upload_file_version=1.0.0
collect_reddit_comment_version=1.0.0
collect_timeline_version=1.0.0
crimson_hexagon_monitors_version=1.0.0
get_personality_version=1.0.0
get_sim_score_version=1.0.0
histogram_version=1.0.0
image_crawler_version=1.0.0
name_entity_recognition_version=1.0.0
network_analysis_version=1.0.0
nginx_version_version=1.0.0
nginx_wo_ssl_version=1.0.0
preprocessing_version=1.0.0
screen_name_prompt_version=1.0.0
sentiment_analysis_version=1.0.0
topic_modeling_version=1.0.0
utku_brand_personality_version=1.0.0

#build images
if [ "$autophrase" = true ] ; then
    docker build -t "$docker_repo"/autophrase:"$autophrase_version" autophrase
    docker push "$docker_repo"/autophrase:"$autophrase_version"
fi



#docker build -t socialmediamacroscope/collect_reddit_comment:latest collect_reddit_comment
#docker build -t socialmediamacroscope/image_crawler:latest image_crawler
#docker build -t socialmediamacroscope/name_entity_recognition:latest name_entity_recognition
#docker build -t socialmediamacroscope/network_analysis:latest network_analysis
#docker build -t socialmediamacroscope/preprocessing:latest preprocessing
#docker build -t socialmediamacroscope/sentiment_analysis:latest sentiment_analysis
#docker build -t socialmediamacroscope/topic_modeling:latest topic_modeling
#docker build -t socialmediamacroscope/smile_server:latest ../../SMILE/www/
