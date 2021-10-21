#!/usr/bin/env python3
"""
Simple Scylla REST API client
Usage::
    ./scylla.py --help [command [args...]]
"""

import argparse
import logging

baselog = logging.getLogger('scylla.cli')
log = logging.getLogger('scylla.cli.util')

from scylla_cli import ScyllaApi, ScyllaApiModule, ScyllaApiCommand, ScyllaApiOption

def list_module(module:ScyllaApiModule):
    print(f"{module.name}:")
    for command in module.commands.keys():
        # FIXME, for now dump the object
        # need to pretty print it
        print(f"{'':4}{command}")

def list_api(scylla_api:ScyllaApi, list_modules:bool, list_module_commands:str):
    if list_modules:
        if list_module_commands:
            raise RuntimeError('--list-modules option cannot be used along with --list-module-commands')
        for name in scylla_api.modules.keys():
            print(f"{name}")
        return

    if list_module_commands:
        try:
            list_module(scylla_api.modules[list_module_commands])
        except KeyError:
            print(f"Error: module '{list_module_commands}' not found")
        return

    first = True
    for module_name in scylla_api.modules.keys():
        list_module(scylla_api.modules[module_name])
        if first:
            print('')
            first = False

def test(node_address:str, port:int) -> ScyllaApi:
    log.debug('Starting test')

    test_command = ScyllaApiCommand('test_command')
    test_command.add_option(ScyllaApiOption('test_positional_option_1', positional=True, help='help for test_positional_option_1'))
    test_command.add_option(ScyllaApiOption('test_option_2', help='help for test_option_2'))

    assert test_command.options[0].name == 'test_positional_option_1'
    assert test_command.options[1].name == 'test_option_2'

    test_module = ScyllaApiModule('test_module')
    test_module.add_command(test_command)

    test_command_1 = ScyllaApiCommand('test_command_1')
    test_command_1.add_option(ScyllaApiOption('test_positional_option_1_1', positional=True, help='help for test_positional_option_1_1'))
    test_command_1.add_option(ScyllaApiOption('test_option_1_2', help='help for test_option_1_2'))
    test_module.add_command(test_command_1)

    assert test_module.commands[0] == test_command
    assert test_module.commands[1] == test_command_1

    test_api = ScyllaApi(node_address=node_address, port=port)
    test_api.add_module(test_module)

    test_module_1 = ScyllaApiModule('test_module_1')
    test_module_1.add_command(test_command_1)
    test_api.add_module(test_module_1)

    log.debug(f"{test_api}")

    assert test_api.modules[0] == test_module
    assert test_api.modules[1] == test_module_1
    assert test_api.modules['test_module'] == test_module
    assert test_api.modules['test_module_1'] == test_module_1

    log.debug('Test done')

    return test_api

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scylla api command line interface.')
    parser.add_argument('-a', '--address', dest='address', type=str, default=ScyllaApi.default_address,
                        help=f"IP address of server node (default: {ScyllaApi.default_address})")
    parser.add_argument('-p', '--port', dest='port', type=int, default=ScyllaApi.default_port,
                        help=f"api port (default: {ScyllaApi.default_port})")

    parser.add_argument('-l', '--list', dest='list_api', action='store_const', const=True, default=False,
                        help=f"List all API commands")
    parser.add_argument('--list-modules', dest='list_modules', action='store_const', const=True, default=False,
                        help=f"List all API modules")
    parser.add_argument('--list-module-commands', dest='list_module_commands', type=str,
                        help=f"List all commands in an API module")

    parser.add_argument('-d', '--debug', dest='debug', action='store_const', const=True, default=False,
                        help=f"Turn on debug logging (default=False)")
    parser.add_argument('-t', '--test', dest='test', action='store_const', const=True, default=False,
                        help=f"Run test (default=False)")

    args = argparse.Namespace()
    parser.parse_args(namespace=args)

    logging.basicConfig(format='%(asctime)s,%(msecs)03d %(process)-7d %(name)-25s %(levelname)-8s | %(message)s')
    baselog.setLevel(logging.DEBUG if args.debug else logging.INFO)

    log.debug('Starting')

    if args.test:
        scylla_api = test(args.address, args.port)
    else:
        # for now
        scylla_api = ScyllaApi()

    if args.list_api or args.list_modules or args.list_module_commands:
        list_api(scylla_api, args.list_modules, args.list_module_commands)

    log.debug('done')
    logging.shutdown()
