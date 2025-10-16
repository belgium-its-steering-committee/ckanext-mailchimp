CKAN_BASE=ckan/ckan-base:2.11
docker run --rm --entrypoint bash -u root -v .:/external "$CKAN_BASE" -lc '
    cd /external
    if ! python setup.py extract_messages; then
        echo "!! Error while extracting strings, extraction cancelled. !!"
        exit 1
    fi
    if ! python setup.py update_catalog --no-fuzzy-matching ; then
        echo "!! Error while updating translations, update cancelled. !!"
        exit 1
    fi
    echo "!! make sure to run compile_translations.sh to update the .mo files after adjusting the missing translations. !!"
  '