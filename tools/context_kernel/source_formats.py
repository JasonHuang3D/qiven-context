"""Strict lossless metadata boundary shared by source adapters and commands."""
import yaml


class StrictLoader(yaml.SafeLoader):
    pass


# Timestamps remain strings; aliases and duplicate keys cannot erase assertions.
StrictLoader.yaml_implicit_resolvers = {
    k: [(tag, rule) for tag, rule in rules if tag != 'tag:yaml.org,2002:timestamp']
    for k, rules in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise ValueError('duplicate or non-string YAML key')
        result[key] = loader.construct_object(value_node)
    return result


StrictLoader.add_constructor('tag:yaml.org,2002:map', _mapping)


def _front(raw):
    text = raw.decode('utf-8')
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        raise ValueError('canonical record missing front matter')
    header, body = text[4:].split('\n---\n', 1)
    if any(isinstance(event, yaml.AliasEvent) for event in yaml.parse(header)):
        raise ValueError('YAML aliases are unsupported in registered records')
    metadata = yaml.load(header, Loader=StrictLoader)
    if not isinstance(metadata, dict):
        raise ValueError('canonical metadata must be a mapping')
    return metadata, body
