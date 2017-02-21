#!/bin/bash
#set -e # halt on error
for folder in $( ls -d */ )
do
    printf "+++++++++++++++++++++++++++++++ \n";
	notebook="$folder/$( ls $folder | grep -v '$(executed_file)$' | grep '$(note_file_ext)$' )"

    printf "Processing $folder...\n";
    check_files;
    file_check=$?
    if [ file_check == 0 ];
    then
    	continue;
    fi;
    if [ file_check == 2 ];
	then
    	continue;
    fi;
    
    if [ ! -f $folder/$executed_file ]; # || [ ! -f $folder/executed_notebook.md ]; # Only run if not already:
    then
        # install requirements
        $( bash backend/$backend/$install_requirements $folder $reqs );
        #printf "\n";
        echo Running notebook $notebook ...;
        $( bash backend/$backend/$execute_note $notebook $folder/$executed_file );
        if [ "$TRAVIS_PULL_REQUEST" == "false" ]; 
        then
            echo "Adding executed notebook to github ...";
            git add $folder/$executed_file;
            git commit -m "new: ${SHA} Executed notebook $notebook";
        fi;
    else
        #printf "\n";
        echo $notebook already run, not rerunning.;
    fi;
    if [ ! -f $folder/zenodo_upload.yml ];
    then
        if [ "$TRAVIS_PULL_REQUEST" == "false" ]; 
        then
            printf "\n";
            echo Uploading $folder to zenodo;
            python zenodo_upload_doi.py $ZENODO_ACCESS $ZENODO_ACCESS_TOKEN $folder/$metadata $folder/$executed_file $folder/$reqs
            git add $folder/zenodo_upload.yml;
            git commit -m "new: $SHA Uploaded to zenodo $folder";
        fi;
    else
        #printf "\n";
        printf "$folder already uploaded\n"; # as \n\n$( cat $folder/zenodo_upload.yml )\n";
    fi;
    printf "+++++++++++++++++++++++++++++++ \n\n";
done;

if [ "$TRAVIS_PULL_REQUEST" == "false" ]; then
    if [ "$CI" == "true" ]; then
        #if [ -z `git diff --exit-code` ]; then
        #    echo "No changes to the output on this push; exiting."
        #    exit 0
        #fi
        git push $SSH_REPO "$TRAVIS_BRANCH";
    else
        echo Updated tree, see git status for details.;
    fi;
fi
