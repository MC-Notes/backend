#!/usr/bin/env python
# encoding: utf-8
# Run a notebook given as first commandline argument in python. Make sure to output to second commandline argument


import sys
import os

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
    
    return '\n'.join(meta_objects), time.strftime("%Y-%m-%d-{}".format('-'.join(meta['title'].split(' '))))
    
    
def main(argv=None):
    argv = sys.argv[1:]
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor
    from nbconvert.preprocessors.execute import CellExecutionError
    from nbconvert.exporters import MarkdownExporter

    notebook = argv[0]
    outfile = argv[1]
    note_folder = os.path.dirname(notebook)
    
    if not os.path.exists(outfile):
        with open(notebook) as f:
            nb = nbformat.read(f, as_version=4)
        #print('Running notebook {} ...'.format(argv[0]))
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        try:
            nb, resources = ep.preprocess(nb, {'metadata': {'path': note_folder}})
        except CellExecutionError as c:
            print(c)
            return 2
        with open(outfile, 'wt') as f:
            nbformat.write(nb, f)    
    else:
        with open(outfile, 'r') as f:
            nb = nbformat.read(f, as_version=4)
    
    header, filename = create_meta_header(note_folder) # Generate metadata header
    # Make blog post with metadata header
    import codecs
    with codecs.open('docs/_posts/{}.md'.format(filename), 'w', 'utf-8') as f:
        # Write a header for the gh-pages website and safe it for later usage
        f.seek(0)
        f.write(header)
        f.write('\n')
    
    if 0: # following some old code for writing markdown exports:
        mdexport = MarkdownExporter()
        from nbconvert.writers import FilesWriter
        mdnb, mdresources = mdexport.from_notebook_node(nb, resources=dict(output_files_dir='images/'.format(filename), encoding='utf-8'))
        fw = FilesWriter(build_directory=note_folder)
        fw.write(mdnb, mdresources, 'executed_notebook')

        # Make blog post
        mdnb, mdresources = mdexport.from_notebook_node(nb, resources=dict(output_files_dir='../assets/posts/images/{}/'.format(filename), encoding='utf-8'))
        fw = FilesWriter(build_directory='docs/_posts/', relpath='../assets/posts/images/{}/'.format(filename))
        fw.write(mdnb, mdresources, filename)
        import codecs
        with codecs.open('docs/_posts/{}.md'.format(filename), 'w', 'utf-8') as f:
            # Write a header for the gh-pages website and safe it for later usage
            f.seek(0)
            f.write(header)
            f.write('\n')
            if 0: # Markdown export not supported yet:
                adjusted_nb = mdnb.replace('{{', '{ {').replace('<!--', '```').replace('-->', '```')
                adjusted_nb = adjusted_nb.replace('../assets', '{{ site.base_url }}{{ site.url }}/assets')
                adjusted_nb = adjusted_nb.replace('$', '$$')
                adjusted_nb = adjusted_nb.replace('$$$', '$$')
                f.write(adjusted_nb)
    return 0

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(2)
