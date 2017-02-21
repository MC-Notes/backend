## Backend repository.
Tags represent a workflow version. 

## Environment variables
Environment variables for backends are available in every script. We source scripts from the main thread to retain environment variables. Variables are:

| variable | description |
|----------|-------------|
| $backend | the backend set in the environment config.yml |
| $workflow_version | the version of workflow to use |
| $notebook | the current notebook being run |
| $note_file_ext | the file extension for notebooks |
| $executed_file | filename for the note after execution |
| $metadata | filename for the metadata yaml file |
| $reqs | filename for requirement files |
| $folder | current notebook folder running |
