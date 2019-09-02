#!/usr/bin/env python3

import re
import yaml
import json
import collections

_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

# Default to OrderedDict 
def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())
def dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))
yaml.add_representer(collections.OrderedDict, dict_representer)
yaml.add_constructor(_mapping_tag, dict_constructor)

# Recursive..
def parse(node, level=1):
    if type(node) is collections.OrderedDict:
        for k, v in node.items():
            yield level, k
            yield from parse(v, level+1)
    elif type(node) is list:
        # only sort if all entries are text
        if all(type(x) is str for x in node):
            node.sort()
        for i in node:
            yield from parse(i, level)
    elif type(node) is str:
        yield None, node
    elif node is None:
        return
    else:
        raise RuntimeError("unknown node type: {}".format(node))

def format(level, field):
    if not level:
        url = None
        m = re.search(r'http\S+', field)
        if m:
            url = m.group(0)
            field = field.replace(url, '').strip('- ')
        name, _, desc = field.partition(' - ')
        if desc:
            desc = ' - ' + desc
        if url:
            name = '[{}]({})'.format(name, url)
        return "- {}{}\n".format(name, desc)
    else:
        return '\n' + '#' * level + ' ' + field + '\n'


def slurp(path):
    with open(path) as fh:
        return fh.read()

if __name__ == "__main__":
    with open('source.yml') as fh:
        blob = yaml.load(fh.read())

    with open('README.md', 'w') as fh:
        fh.write(slurp('.header.md'))
        for level, field in parse(blob, 1):
            fh.write(format(level, field))
        fh.write(slurp('.footer.md'))