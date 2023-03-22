# set repository
docker_repo=socialmediamacroscope

# set build and push option
build=true
push=false

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
image_crawler=true
name_entity_recognition=true
network_analysis=true
nginx=false
nginx_wo_ssl=false
preprocessing=false
screen_name_prompt=false
sentiment_analysis=false
topic_modeling=false
utku_brand_personality=false

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

#build images
if [ "$autophrase" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/autophrase:"$autophrase_version" autophrase
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/autophrase:"$autophrase_version"
  fi
fi

if [ "$biometer_check_bot" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/biometer_check_bot:"$biometer_check_bot_version" biometer_check_bot
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/biometer_check_bot:"$biometer_check_bot_version"
  fi
fi

if [ "$bulk_comparison" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/bulk_comparison:"$bulk_comparison_version" bulk_comparison
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/bulk_comparison:"$bulk_comparison_version"
  fi
fi

if [ "$check_screen_name" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/check_screen_name:"$check_screen_name_version" check_screen_name
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/check_screen_name:"$check_screen_name_version"
  fi
fi

if [ "$classification_predict" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/classification_predict:"$classification_predict_version" classification_predict
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/classification_predict:"$classification_predict_version"
  fi
fi

if [ "$classification_split" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/classification_split:"$classification_split_version" classification_split
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/classification_split:"$classification_split_version"
  fi
fi

if [ "$classification_train" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/classification_train:"$classification_train_version" classification_train
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/classification_train:"$classification_train_version"
  fi
fi

if [ "$clowder_create_collection" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/clowder_create_collection:"$clowder_create_collection_version" clowder_create_collection
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/clowder_create_collection:"$clowder_create_collection_version"
  fi
fi

if [ "$clowder_create_dataset" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/clowder_create_dataset:"$clowder_create_dataset_version" clowder_create_dataset
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/clowder_create_dataset:"$clowder_create_dataset_version"
  fi
fi

if [ "$clowder_create_space" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/clowder_create_space:"$clowder_create_space_version" clowder_create_space
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/clowder_create_space:"$clowder_create_space_version"
  fi
fi

if [ "$clowder_list" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/clowder_list:"$clowder_list_version" clowder_list
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/clowder_list:"$clowder_list_version"
  fi
fi

if [ "$clowder_upload_file" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/clowder_upload_file:"$clowder_upload_file_version" clowder_upload_file
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/clowder_upload_file:"$clowder_upload_file_version"
  fi
fi

if [ "$collect_reddit_comment" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/collect_reddit_comment:"$collect_reddit_comment_version" collect_reddit_comment
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/collect_reddit_comment:"$collect_reddit_comment_version"
  fi
fi

if [ "$collect_timeline" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/collect_timeline:"$collect_timeline_version" collect_timeline
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/collect_timeline:"$collect_timeline_version"
  fi
fi

if [ "$crimson_hexagon_monitors" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/crimson_hexagon_monitors:"$crimson_hexagon_monitors_version" crimson_hexagon_monitors
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/crimson_hexagon_monitors:"$crimson_hexagon_monitors_version"
  fi
fi

if [ "$get_personality" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/get_personality:"$get_personality_version" get_personality
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/get_personality:"$get_personality_version"
  fi
fi

if [ "$get_sim_score" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/get_sim_score:"$get_sim_score_version" get_sim_score
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/get_sim_score:"$get_sim_score_version"
  fi
fi

if [ "$histogram" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/histogram:"$histogram_version" histogram
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/histogram:"$histogram_version"
  fi
fi

if [ "$image_crawler" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/image_crawler:"$image_crawler_version" image_crawler
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/image_crawler:"$bimage_crawler_version"
  fi
fi

if [ "$name_entity_recognition" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/name_entity_recognition:"$name_entity_recognition_version" name_entity_recognition
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/name_entity_recognition:"$name_entity_recognition_version"
  fi
fi

if [ "$network_analysis" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/network_analysis:"$network_analysis_version" network_analysis
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/network_analysis:"$network_analysis_version"
  fi
fi

if [ "$nginx" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/nginx:"$nginx_version" nginx
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/nginx:"$nginx_version"
  fi
fi

if [ "$nginx_wo_ssl" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/nginx_wo_ssl:"$nginx_wo_ssl_version" nginx_wo_ssl
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/nginx_wo_ssl:"$nginx_wo_ssl_version"
  fi
fi

if [ "$preprocessing" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/preprocessing:"$preprocessing_version" preprocessing
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/preprocessing:"$preprocessing_version"
  fi
fi

if [ "$screen_name_prompt" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/screen_name_prompt:"$screen_name_prompt_version" screen_name_prompt
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/screen_name_prompt:"$screen_name_prompt_version"
  fi
fi

if [ "$sentiment_analysis" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/sentiment_analysis:"$sentiment_analysis_version" sentiment_analysis
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/sentiment_analysis:"$sentiment_analysis_version"
  fi
fi

if [ "$topic_modeling" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/topic_modeling:"$topic_modeling_version" topic_modeling
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/topic_modeling:"$topic_modeling_version"
  fi
fi

if [ "$utku_brand_personality" = true ] ; then
  if ["$build" = true] ; then
    docker build -t "$docker_repo"/utku_brand_personality:"$utku_brand_personality_version" utku_brand_personality
  fi
  if ["$push" = true] ; then
    docker push "$docker_repo"/utku_brand_personality:"$utku_brand_personality_version"
  fi
fi
