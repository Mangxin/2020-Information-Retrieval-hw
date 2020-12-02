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

}


loopname=_stem3
Index_name=id_meta_gs_stem3_dfr2


Source_index_name=id_meta$loopname
Type_name=meta_id$loopname

echo "Index_name: "$Index_name
echo "Type_name: "$Type_name
echo "Source_index_name: "$Source_index_name

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
                        \"basic_model\": \"ine\",
                        \"after_effect\": \"b\",
                        \"normalization\": \"z\"
                    }
                }
            }
        }
    }'"
echo $cmd | sh
IndexTest $Index_name $Type_name $Source_index_name




