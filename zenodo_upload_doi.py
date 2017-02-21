import yaml, requests, sys, json, os

argv = sys.argv[1:]

try:
    url, access_token, metadata_file, notebook, requirements = argv
except:
    print('Usage: python zenodo_upload_doi.py zenodo_url zenodo_access_token metadata_file executed_notebook_file requirements_file \n upload to zenodo url with access token with metadata stored as .yml file in metadata_file. ')
    sys.exit(2)

folder = os.path.dirname(notebook)

###############
# Make sure metadata constains necessary info
headers = {"Content-Type": "application/json"}
with open(metadata_file) as f:
    metadata = yaml.load(f)

if str(metadata['accepted']).lower() in ['true', 'yes', 'y']:
    metadata.setdefault('upload_type', 'publication')
    metadata.setdefault('publication_type', 'other')
    metadata.setdefault('access_right', 'open')

    del metadata['accepted']
    del metadata['notebook_url']
    del metadata['date']

    import time
    l = time.localtime()
    metadata.setdefault('publication_date', "{tm_year}-{tm_mon:>02}-{tm_mday:>02}".format(tm_year=l.tm_year, tm_mon=l.tm_mon, tm_mday=l.tm_mday))
    ###############

    # simple check for metadata
    def check_metadata(metadata):
        if isinstance(metadata, str):
            return True
        elif isinstance(metadata, dict):
            return all(map(check_metadata, metadata.values()))
        elif isinstance(metadata, list):
            return all(map(check_metadata, metadata))
        raise AttributeError('Type mismatch in given metadata: {} of type {!s}'.format(metadata, type(metadata)))
    check_metadata(metadata)

    # Make small script to add access token to urls:
    def access(url):
        return '{}?access_token={}'.format(url, access_token)

    # create deposition
    c_url = access(url)

    r = requests.post(c_url, data=json.dumps(dict(metadata=metadata)), headers=headers)
    r_json = r.json()

    # check deposition status
    if r.status_code != 201:
        # deposition failed, report status
        stat = 'Given metadata returned error code {}'.format(r_json['status'])
        if 'message' in r_json:
            stat = "{} with message {}".format(stat, r_json['message'])
        if 'errors' in r_json:
            stat = "{}\n{!s}".format(stat, r_json['errors'])
        raise AttributeError(stat)
        sys.exit(r_json['status'])
    else:
        # deposition success:
        post_url = access(r_json['links']['files'])
        # add notebook and requirements to deposition
        with open(notebook, 'rb') as f:
            data = {'filename': 'notebook.ipynb'}
            files = {'file': f}
            r = requests.post(post_url, data=data, files=files)
            
        with open(requirements, 'rb') as f:
            data = {'filename': 'requirements.txt'}
            files = {'file': f}
            r = requests.post(post_url, data=data, files=files)

        with open(metadata_file, 'rb') as f:
            data = {'filename': 'requirements.txt'}
            files = {'file': f}
            r = requests.post(post_url, data=data, files=files)
        
        # publish the deposition on zenodo
        pub_url = access(r_json['links']['publish'])
        import pprint
        r = requests.post(pub_url)
        pprint.pprint(r.json())
        
        with open(os.path.join(folder, 'zenodo_upload.yml'), 'w') as f:
            yaml.dump(r.json(), f)
            
else:
    print("Notebook not accepted, accept by setting accepted=True in metadata.yaml")