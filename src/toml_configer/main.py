from toml_configer.configer import *

if __name__ == "__main__":
    # load the config file
    # and print the tree of the config file
    config = load("config.toml")
    print(get(config, generate_tree=True))

    # try to add a new path to the config file
    # and print the tree of the config file
    set(config, "connections.dev.public_host", "public_host")
    print(get(config, generate_tree=True))

    # try to remove a path from the config file
    # and print the tree of the config file
    remove(config, "connections.dev.public_host")
    print(get(config, generate_tree=True))

    # save the config file
    save(config, "config.toml")
