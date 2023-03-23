# set repository
docker_repo=socialmediamacroscope

# set build and push option
build=true
push=true

# set components selection
autophrase=true
biometer_check_bot=true
bulk_comparison=true
check_screen_name=true
classification_predict=true
classification_split=true
classification_train=true
clowder_create_collection=true
clowder_create_dataset=true
clowder_create_space=true
clowder_list=true
clowder_upload_file=true
collect_reddit_comment=true
collect_timeline=true
crimson_hexagon_monitors=true
get_personality=true
get_sim_score=true
histogram=true
image_crawler=true
name_entity_recognition=true
network_analysis=true
nginx=true
nginx_wo_ssl=true
preprocessing=true
screen_name_prompt=true
sentiment_analysis=true
topic_modeling=true
utku_brand_personality=true

# set version numbers
autophrase_version=1.0.0
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

function build_and_push ()
{
  image_name=$1
  image_version=$2
  docker_repo=$3
  if [ "$build" = true ]; then
    echo "docker build -t $3/$1:$2 $1"
#    docker build -t "$3"/"$1":"$2" "$1"
  fi
  if [ "$push" = true ]; then
    echo "docker push $3/$1:$2"
#    docker push "$3"/"$1":"$2"
  fi
}

#build images
if [ "$autophrase" = true ]; then
  build_and_push autophrase $autophrase_version $docker_repo
fi

if [ "$biometer_check_bot" = true ]; then
  build_and_push biometer_check_bot $biometer_check_bot_version $docker_repo
fi

if [ "$bulk_comparison" = true ]; then
  build_and_push bulk_comparison $bulk_comparison_version $docker_repo
fi

if [ "$check_screen_name" = true ]; then
  build_and_push check_screen_name $check_screen_name_version $docker_repo
fi

if [ "$classification_predict" = true ]; then
  build_and_push autoclassification_predictphrase $classification_predict_version $docker_repo
fi

if [ "$classification_split" = true ]; then
  build_and_push classification_split $classification_split_version $docker_repo
fi

if [ "$classification_train" = true ]; then
  build_and_push classification_train $classification_train_version $docker_repo
fi

if [ "$clowder_create_collection" = true ]; then
  build_and_push clowder_create_collection $clowder_create_collection_version $docker_repo
fi

if [ "$clowder_create_dataset" = true ]; then
  build_and_push clowder_create_dataset $clowder_create_dataset_version $docker_repo
fi

if [ "$clowder_create_space" = true ]; then
  build_and_push clowder_create_space $clowder_create_space_version $docker_repo
fi

if [ "$clowder_list" = true ]; then
  build_and_push clowder_list $clowder_list_version $docker_repo
fi

if [ "$clowder_upload_file" = true ]; then
  build_and_push clowder_upload_file $clowder_upload_file_version $docker_repo
fi

if [ "$collect_reddit_comment" = true ]; then
  build_and_push collect_reddit_comment $collect_reddit_comment_version $docker_repo
fi

if [ "$collect_timeline" = true ]; then
  build_and_push collect_timeline $collect_timeline_version $docker_repo
fi

if [ "$crimson_hexagon_monitors" = true ]; then
  build_and_push crimson_hexagon_monitors $crimson_hexagon_monitors_version $docker_repo
fi

if [ "$get_personality" = true ]; then
  build_and_push get_personality $get_personality_version $docker_repo
fi

if [ "$get_sim_score" = true ]; then
  build_and_push get_sim_score $get_sim_score_version $docker_repo
fi

if [ "$histogram" = true ]; then
  build_and_push histogram $histogram_version $docker_repo
fi

if [ "$image_crawler" = true ]; then
  build_and_push image_crawler $image_crawler_version $docker_repo
fi

if [ "$name_entity_recognition" = true ]; then
  build_and_push name_entity_recognition $name_entity_recognition_version $docker_repo
fi

if [ "$network_analysis" = true ]; then
  build_and_push network_analysis $network_analysis_version $docker_repo
fi

# nginx doesn't work since the word nginx makes an error
#if [ "$nginx" = true ]; then
#  build_and_push nginx $nginx_version $docker_repo
#fi

if [ "$nginx_wo_ssl" = true ]; then
  build_and_push nginx_wo_ssl $nginx_wo_ssl_version $docker_repo
fi

if [ "$preprocessing" = true ]; then
  build_and_push preprocessing $preprocessing_version $docker_repo
fi

if [ "$screen_name_prompt" = true ]; then
  build_and_push screen_name_prompt $screen_name_prompt_version $docker_repo
fi

if [ "$sentiment_analysis" = true ]; then
  build_and_push sentiment_analysis $sentiment_analysis_version $docker_repo
fi

if [ "$topic_modeling" = true ]; then
  build_and_push topic_modeling $topic_modeling_version $docker_repo
fi

if [ "$utku_brand_personality" = true ]; then
  build_and_push utku_brand_personality $utku_brand_personality_version $docker_repo
fi
