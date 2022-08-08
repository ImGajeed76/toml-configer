import click
from toml_configer.configer import *


@click.group()
def cli():
    pass


if __name__ == "__main__":
    config = load("config.toml")
    print(get(config, generate_tree=True))

    set(config, "connections.dev.host", "publichost")
    print(get(config, generate_tree=True))

    remove(config, "connections.dev.host")
    print(get(config, generate_tree=True))

    save(config, "config.toml")
