def create_meta_header(folder):
    """
    Add metadata to a converted markdown notebook
    """
    import yaml
    with open('{}/metadata.yml'.format(folder), 'r') as f:
        meta = yaml.load(f)
        
    meta_objects = ["---"]
    def _add_meta(meta, key, meta_objects, meta_key=None):
        if key in meta:
            meta_key = meta_key or key
            meta_value = meta[key]
            if type(meta_value) is list:
                meta_value = str(map(lambda x: '{}'.format(x), map(str, meta_value)))
            else:
                meta_value = '\"{}\"'.format(meta_value)
            meta_objects.append('{}: {}'.format(meta_key, meta_value))

    meta_objects.append('layout: \"page\"')
    _add_meta(meta, 'title', meta_objects)
    _add_meta(meta, 'description', meta_objects)

    import time
    meta['date'] = time.strftime("%Y-%m-%d %H:%M:%S %z")
    _add_meta(meta, 'date', meta_objects)
    
    _add_meta(meta, 'keywords', meta_objects, meta_key='categories')
    
    meta.setdefault('accepted', 'false')
    _add_meta(meta, 'accepted', meta_objects)
    
    meta.setdefault('notebook_url', '{}/executed_notebook.ipynb'.format(folder))
    _add_meta(meta, 'notebook_url', meta_objects)
    
    meta_objects.append('---')
    
    with open('{}/metadata.yml'.format(folder), 'w') as f:
        yaml.dump(meta, f)
    
    return '\n'.join(meta_objects), time.strftime("%Y-%m-%d-{}".format('-'.join(meta['title'].split(' ')))), meta


if __name__ == "__main__":
    argv = sys.argv[1:]
    import nbformat, os
    from nbconvert.preprocessors import ExecutePreprocessor
    from nbconvert.preprocessors.execute import CellExecutionError
    from nbconvert.exporters import MarkdownExporter

    note_folder = argv[0]

    header, filename, meta_data = create_meta_header(note_folder) # Generate metadata header
    # Make blog post with metadata header

    import codecs
    outfolder='_under_review'
    if meta_data['accepted']:
        reviewpath = 'docs/{}/{}.md'.format(out_folder, meta_data['title'])
        if os.path.exists(reviewpath):
            os.remove(reviewpath)
        outfolder='_accepted' # put the new file into accepted
    outpath = 'docs/{}/{}.md'.format(out_folder, meta_data['title'])
    with codecs.open(outpath, 'w', 'utf-8') as f:
        # Write a header for the gh-pages website and safe it for later usage
        f.seek(0)
        f.write(header)
        f.write('\n')

    import subprocess
    subprocess.call(["git", "add", reviewpath, outpath])
    