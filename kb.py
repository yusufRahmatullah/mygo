#!/usr/bin/python
from argparse import ArgumentParser
import os
import subprocess as sp
import sys

# Known kubectl commands
KB_COMMANDS = ['pods', 'hpa', 'deployment', 'exec', 'edit']


def parse_args():
    try:
        parser = ArgumentParser(description='Simplify kubectl command')
        parser.add_argument(
            'keywords', nargs='+',
            help=f'kubectl command arguments {{{" ".join(KB_COMMANDS)}}}'
        )
        return parser.parse_args()
    except Exception:
        parser.print_help()
        exit(1)


def _cmd(cmd):
    res = sp.check_output(cmd, shell=True)
    return res.decode('utf-8')


def _extract_service_pod(another_keys):
    if len(another_keys) > 2:
        print(f'Multiple kubectl arguments: {" ".join(another_keys)}')
        exit(1)
    service = ''
    pod = ''
    k1, k2 = another_keys
    if k1.count('-') > k2.count('-'):
        pod = k1
        service = k2
    else:
        pod = k2
        service = k1
    return service, pod


def _validate_kb_cmd(cmd_keys):
    if len(cmd_keys) > 2:
        print(f'Commands too much')
        exit(1)
    if len(cmd_keys) == 2:
        if 'edit' not in cmd_keys:
            print(f'Multiple cmd keys: {" ".join(cmd_keys)}')
            exit(1)
        if 'edit' in cmd_keys and ['pods', 'exec'] in cmd_keys:
            another_cmd = [x for x in cmd_keys if x != 'edit'][0]
            print(f'Cannot edit {another_cmd}')
            exit(1)
        if len(set(cmd_keys)) == 1:
            print(f'Duplicate command: {cmd_keys[0]}')
            exit(1)
    if len(cmd_keys) == 1 and 'edit' == cmd_keys[0]:
        print('Cannot edit without another command')
        exit(1)
    if len(cmd_keys) == 0:
        print(f'No kubectl command. Choice: {{{" ".join(KB_COMMANDS)}}}')
        exit(1)


def _process_kb_get(cmd, another_keys):
    if len(another_keys) == 0:
        print('No service found')
        exit(1)
    service = another_keys[0]
    out = _cmd(f'kubectl -n {service} get {cmd}')
    print(out)


def _process_kb_edit(cmd, another_keys):
    service, pod = _extract_service_pod(another_keys)
    _cmd(
        f'KUBE_EDITOR=nano kubectl -n {service} edit {cmd} {pod}'
    )


def _process_kb_exec(another_keys):
    service, pod = _extract_service_pod(another_keys)
    _cmd(
        f'kubectl -n {service} exec -it {pod} -- sh'
    )


def _process_kb_cmd(cmd_keys, another_keys):
    if len(cmd_keys) == 1:
        cmd = cmd_keys[0]
        if cmd == 'exec':
            _process_kb_exec(another_keys)
            return
        if len(another_keys) > 1:
            print(f'Multiple service detected: {" ".join(another_keys)}')
            exit(1)
        _process_kb_get(cmd, another_keys)
    else:
        cmd = [x for x in cmd_keys if x != 'edit'][0]
        _process_kb_edit(cmd, another_keys)


def process(args):
    cmd_keys = []
    another_keys = []
    for key in args.keywords:
        if key in KB_COMMANDS:
            cmd_keys.append(key)
        else:
            another_keys.append(key)
    _validate_kb_cmd(cmd_keys)
    _process_kb_cmd(cmd_keys, another_keys)


def main():
    args = parse_args()
    process(args)


if __name__ == '__main__':
    main()
