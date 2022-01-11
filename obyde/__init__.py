# -*- coding: utf-8 -*-

import argparse
import os
import re
import string
import sys
from collections import defaultdict
from hashlib import sha256

import frontmatter
import yaml

from .parsing import parse_content_blocks
from .rewriting import RewritingEngine, RewritingPipeline
from .rewriting.highlight import ObsidianHighlightRewritingTransformer
from .util import parse_obsidian_links, slugify_md_filename

__all__ = ['main']


def parse_args():
    parser = argparse.ArgumentParser(prog=__package__,
                                     description='Moves and process markdown vaults (mainly Obsidian) to a publishable format')
    parser.add_argument('-c', '--config', type=str, required=True,
                        help='Path to yaml config file. Check config.sample.yaml for an example.')
    return parser.parse_args()


def load_config(config_path):
    try:
        with open(config_path, 'r') as fs:
            config = yaml.safe_load(fs)
            return config
    except:
        raise ValueError(
            'Failed to load configuration. Is the file path correct?')


def dir_exists_or_raise(dirpath, dirpath_type):
    if not os.path.exists(dirpath) or not os.path.isdir(dirpath):
        raise ValueError(
            f'{dirpath} - {dirpath_type} does not exist or is not a directory')
    return dirpath


def find_files(dirpath, ext='', exclusions=[]):
    dirpath = os.path.abspath(dirpath)
    dirpath = dir_exists_or_raise(dirpath, 'input files location')
    index = defaultdict(set)

    if exclusions:
        exclusions = list(
            map(lambda exc: os.path.join(dirpath, exc), exclusions))

    def filefilter(f):
        correct_extension = (ext and f.endswith(ext)) or (not ext)
        return correct_extension

    def excluded_dir(d):
        return any(map(lambda exc: exc in os.path.commonpath([exc, d]), exclusions))

    for root, _, files in os.walk(dirpath, followlinks=False):
        filtered_files = filter(filefilter, files)

        if excluded_dir(root):
            continue

        for f in filtered_files:
            index[f].add(os.path.join(root, f))

    for x, p in index.items():
        if len(p) > 1:
            filenames = ','.join(p)
            raise ValueError(
                f'Filename collision detected for {filenames}. This is currently not a supported operating mode.')

    cleaned_index = {}

    for x, p in index.items():
        cleaned_index[x] = p.pop()

    return cleaned_index


def generate_post_link(dated_name, post_link_mode):
    if post_link_mode == 'jekyll':
        return f'{{% post_url {dated_name} %}}'
    elif post_link_mode == 'hugo':
        return f'{{{{< relref "{dated_name}" >}}}}'
    else:
        raise ValueError(f'Unknown post link mode: {post_link_mode}')


def find_replace(content, metadata):
    find_list = metadata.get("find")
    replace_list = metadata.get("replace")

    if not (find_list and replace_list):
        return content

    if len(find_list) != len(replace_list):
        raise ValueError(
            f'Length of with list is not the same as the length of the replace list')

    rewritten = content
    for i in range(len(find_list)):
        find_regex = re.compile(find_list[i])
        replace_string = replace_list[i]
        rewritten = re.sub(find_regex, replace_string, rewritten)

    return rewritten


def rewrite_links(content, dated_file_index, asset_index, relative_asset_path_prefix, post_link_mode):
    obsidian_links = parse_obsidian_links(content)
    rewritten = content
    for link in obsidian_links:
        link_text = link.replace('[[', '').replace(']]', '')
        link_target = link_text
        if '|' in link_text:
            split_link = link_text.split('|')
            link_target = split_link[0]
            link_text = split_link[1] if len(split_link) > 1 else ''
        written = False
        for filename, filepaths in asset_index.items():
            oldpath, newpath = filepaths
            if link_target in filename or link_target in oldpath:
                rewritten = rewritten.replace(
                    link, f'[{link_text}]({relative_asset_path_prefix}/{newpath})')
                written = True
                break
        if not written:
            link_name_slug = slugify_md_filename(link_target)
            dated_name, _, _ = dated_file_index.get(
                link_name_slug, (None, None, None))
            if dated_name:
                rewritten = rewritten.replace(
                    link, f'[{link_text}]({generate_post_link(dated_name, post_link_mode)})')
    return rewritten


def write_asset_files(asset_files, asset_output_path):
    modified_file_paths = {}
    for name, path in asset_files.items():
        data = b''
        extension = os.path.splitext(path)[1]
        with open(path, 'rb') as fs:
            data = fs.read()
        hashed_fname = sha256(data).hexdigest() + extension
        asset_path = os.path.join(asset_output_path, hashed_fname)
        if not os.path.exists(asset_path):
            with open(asset_path, 'wb') as out:
                out.write(data)
        modified_file_paths[name] = (path, hashed_fname)
    return modified_file_paths


def validate_postdate(path, postdate):
    if not postdate:
        raise ValueError(
            f'Post at {path} does not have a date, please add a date to the frontmatter.')

    components = tuple(postdate.split('-'))
    try:
        assert len(components) == 3
        year, month, day = components
        for comp in [year, month, day]:
            assert all(map(lambda x: x in string.digits, comp))
    except AssertionError:
        raise ValueError(
            'Invalid frontmatter date format! Expected format is YYYY-MM-DD')
    return postdate


def rewrite_post_with_engine(engine: RewritingEngine, post):
    post_content = post.content
    post.content = ""
    post_metadata = frontmatter.dumps(post)
    post_content_blocks = parse_content_blocks(post_content)

    post_metadata, post_content = engine.rewrite(
        post_metadata, post_content_blocks)
    post_text = "\n".join([post_metadata, post_content])
    post = frontmatter.loads(post_text)
    return post


def process_vault(config):
    md_files = find_files(config['vault']['path'], ext='.md',
                          exclusions=config['vault'].get('excluded_subdirectories', []))
    asset_files = find_files(config['vault']['asset_path'])
    post_output_path = dir_exists_or_raise(
        config['output']['post_output_path'], 'post output path')
    asset_output_path = dir_exists_or_raise(
        config['output']['asset_output_path'], 'asset output path')
    relative_asset_path_prefix = config['output'].get(
        'relative_asset_path_prefix', '{{ site.assets_location }}')
    post_link_mode = config['output'].get('post_link_mode', 'jekyll')
    if not post_link_mode in ['jekyll', 'hugo']:
        raise ValueError(
            f'Unknown post link mode "{post_link_mode}". must be set to either "jekyll" or "hugo".')

    copied_asset_files = write_asset_files(asset_files, asset_output_path)

    dated_files = {}
    post_map = {}
    for name, path in md_files.items():
        name, ext = os.path.splitext(name)
        slug_name = slugify_md_filename(name)
        post = frontmatter.load(path)
        postdate = validate_postdate(path, str(post.metadata.get('date', '')))
        dated_name = postdate + '-' + slug_name
        dated_name_ext = dated_name + ext
        dated_files[slug_name] = (dated_name, dated_name_ext, path)
        post_map[slug_name] = post

    rewriting_pipeline = RewritingPipeline([
        ObsidianHighlightRewritingTransformer()
    ])
    rewrite_engine = RewritingEngine(transformer=rewriting_pipeline)

    for slug_name, data in dated_files.items():
        _, dated_name_ext, path = data
        post = post_map[slug_name]

        # Allow find_replace to run on metadata in addition to post content
        post_text = find_replace(frontmatter.dumps(post), post.metadata)
        post = frontmatter.loads(post_text)
        post = rewrite_post_with_engine(rewrite_engine, post)

        rewritten = rewrite_links(
            post.content, dated_files, copied_asset_files, relative_asset_path_prefix, post_link_mode)
        post.content = rewritten
        with open(os.path.join(post_output_path, dated_name_ext),  'wb') as out:
            frontmatter.dump(post, out)


def main():
    try:
        args = parse_args()
        config = load_config(args.config)
        process_vault(config)
    except ValueError as e:
        print(f'Error: {e}', file=sys.stderr)
