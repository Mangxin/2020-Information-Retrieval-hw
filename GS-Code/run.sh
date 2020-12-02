
IndexTest(){
    # $Index_name - 1
    # $Type_name - 2
    # $Source_index_name - 3
    echo "\n============================================================================"
    echo "                similarity function into Index                         "
    echo ============================================================================

    echo $1 $2 $3
     

    # * 对比函数写入index
    curl -H "Content-Type: application/json" -XPUT http://localhost:9200/$1/_mapping/$2 -d'
    {
        "properties" : {
            "abstract" : {
            "type" : "text",
            "similarity": "my_similarity",
            "fields" : {
                "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
                }
            }
            },
            "id" : {
            "type" : "text",
            "similarity": "my_similarity",
            "fields" : {
                "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
                }
            }
            },
            "title" : {
            "type" : "text",
            "similarity": "my_similarity",
            "fields" : {
                "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
                }
            }
            }
        }
    }'

    echo "\n============================================================================"
    echo "                               copy index                                "
    echo ============================================================================

    # * 拷贝数据

    cmd="curl -H \"Content-Type: application/json\" -XPOST http://localhost:9200/_reindex/ -d '
    {
      \"source\": {
        \"index\": \"$3\"
      },
      \"dest\": {
        \"index\": \"$1\"
      }
    }'"

    echo $cmd | sh

    cmd="python search.py --index3=$1 --doc_type3=$2"
    echo $cmd | sh

    . ./compare.sh

}


Index_name=id_meta_gs_try_auto

# for loopname in ' ' _stop _stem _stem2 _stem3 _lower 
for loopname in _stem2 _stem3 _stem
do
    echo "**********************************************************************************************************************"
    echo "**********************************************************************************************************************"

    Source_index_name=id_meta$loopname
    Type_name=meta_id$loopname

    echo "Index_name: "$Index_name
    echo "Type_name: "$Type_name
    echo "Source_index_name: "$Source_index_name

    

    for score_function in BM25 DFR DFI IB
    do
        if [ "$score_function" = "BM25" ]
        then
            for k1 in 1 1.2 1.5
            do
                for b in 0 0.25 0.5 0.75 1
                do
                    echo "\n============================================================================"
                    echo "                                Delete Index                              "
                    echo ============================================================================
                    # delete former index
                    curl -X DELETE http://localhost:9200/$Index_name

                    echo "\n============================================================================"
                    echo "                                Create Index                              "
                    echo ============================================================================

                    cmd="curl -H \"Content-Type: application/json\" -XPUT http://localhost:9200/$Index_name -d'
                        {
                            \"settings\": {
                                \"index\": {
                                \"similarity\": {
                                        \"my_similarity\": {
                                            \"type\": \"BM25\",
                                            \"k1\": $k1,
                                            \"b\": $b,
                                            \"discount_overlaps\": \"true\"
                                        }
                                    }
                                }
                            }
                        }'"
                    echo $cmd | sh

                    echo "\n *Setting*: $score_function $k1 $b"
                    IndexTest $Index_name $Type_name $Source_index_name
                
                done
            done
        elif [ "$score_function" = "DFR" ]
        then
            for basic_model in "g" "if" "in" "ine"
            do
                for after_effect in "b" "l"
                do
                    for normalization in no h1 h2 h3 z
                    do
                        echo "\n============================================================================"
                        echo "                                Delete Index                              "
                        echo ============================================================================
                        # delete former index
                        curl -X DELETE http://localhost:9200/$Index_name

                        echo "\n============================================================================"
                        echo "                                Create Index                              "
                        echo ============================================================================


                        cmd="curl -H \"Content-Type: application/json\" -XPUT http://localhost:9200/$Index_name -d'
                            {
                                \"settings\": {
                                    \"index\": {
                                    \"similarity\": {
                                            \"my_similarity\": {
                                                \"type\": \"DFR\",
                                                \"basic_model\": \"$basic_model\",
                                                \"after_effect\": \"$after_effect\",
                                                \"normalization\": \"$normalization\"
                                            }
                                        }
                                    }
                                }
                            }'"
                        echo $cmd | sh

                        echo "\n *Setting*: $score_function $basic_model $after_effect $normalization"
                        IndexTest $Index_name $Type_name $Source_index_name

                    done
                done
            done

        elif [ "$score_function" = "DFI" ]
        then
            for independence_measure in standardized saturated chisquared
            do
                if [ "$loopname" != "_stop" ]
                then
                    echo "\n============================================================================"
                        echo "                                Delete Index                              "
                        echo ============================================================================
                        # delete former index
                        curl -X DELETE http://localhost:9200/$Index_name

                        echo "\n============================================================================"
                        echo "                                Create Index                              "
                        echo ============================================================================
                    # DFI not remove stop words  - 
                    cmd="curl -H \"Content-Type: application/json\" -XPUT http://localhost:9200/$Index_name -d'
                    {
                        \"settings\": {
                            \"index\": {
                            \"similarity\": {
                                    \"my_similarity\": {
                                        \"type\": \"DFI\",
                                        \"independence_measure\": \"$independence_measure\"
                                    }
                                }
                            }
                        }
                    }'"
                    echo $cmd | sh

                    echo "\n *Setting*: $score_function $independence_measure"
                    IndexTest $Index_name $Type_name $Source_index_name
                fi
            done

        elif [ "$score_function" = "IB" ]
        then
            for distribution in ll spl
            do
                for lambda in df ttf
                do
                    for normalization in no h1 h2 h3 z
                    do
                        echo "\n============================================================================"
                        echo "                                Delete Index                              "
                        echo ============================================================================
                        # delete former index
                        curl -X DELETE http://localhost:9200/$Index_name

                        echo "\n============================================================================"
                        echo "                                Create Index                              "
                        echo ============================================================================

                        cmd="curl -H \"Content-Type: application/json\" -XPUT http://localhost:9200/$Index_name -d'
                            {
                                \"settings\": {
                                    \"index\": {
                                    \"similarity\": {
                                            \"my_similarity\": {
                                                \"type\": \"IB\",
                                                \"distribution\": \"$distribution\",
                                                \"lambda\": \"$lambda\",
                                                \"normalization\": \"$normalization\"
                                            }
                                        }
                                    }
                                }
                            }'"
                        echo $cmd | sh

                        echo "\n *Setting*: $score_function $distribution $lambda $normalization"
                        IndexTest $Index_name $Type_name $Source_index_name
                    done
                done
            done

        fi


    done

done





