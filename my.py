#!/c/Users/Yusuf/anaconda3/python
from argparse import ArgumentParser
import os
import subprocess as sp
import sys

KNOWN_FILES = 'known_gs.txt'
# Statuses
GIT_ADDED = 'Git-added'
NOT_ADDED = 'Not git-added'
UNTRACKED = 'Untracked'
# Known kubectl commands
KB_COMMANDS = ['pods', 'hpa', 'deployment', 'exec', 'edit']


def _parse_gs(subparsers):
    parser = subparsers.add_parser('gs', help='Simplified Git Status')
    parser.add_argument(
        '-s', '--short', action='store_true',
        help='Show file name only'
    )
    gs_subparsers = parser.add_subparsers(dest='subcmd')
    gs_subparsers.add_parser('add', help='Git add all changes')
    gs_subparsers.add_parser('diff', help='Git diff all changes')
    gen_parser = gs_subparsers.add_parser(
        'gen', help=f'Generate {KNOWN_FILES} file'
    )
    gen_subparsers = gen_parser.add_subparsers(dest='gencmd')
    gen_add_parser = gen_subparsers.add_parser(
        'add', help=f'Add file to {KNOWN_FILES}'
    )
    gen_add_parser.add_argument(
        'file', help='File that will be whitelisted'
    )


def parse_args():
    try:
        parser = ArgumentParser(
            description='Simple Utility for daily tasks'
        )
        subparsers = parser.add_subparsers(dest='cmd')
        subparsers.required = True
        _parse_gs(subparsers)
        return parser.parse_args()
    except Exception:
        parser.print_help()
        sys.exit(2)


def _cmd(cmd):
    res = sp.check_output(cmd, shell=True)
    return res.decode('utf-8')


def _get_branch():
    return _cmd('git rev-parse --abbrev-ref HEAD').strip()


def _extract_status(line):
    work = line[1]
    file = line[3:]
    key = GIT_ADDED
    if work == '?':
        key = UNTRACKED
    elif work != ' ':
        key = NOT_ADDED
    return key, file


def _known_files():
    if not os.path.exists(KNOWN_FILES):
        return []
    with open(KNOWN_FILES) as f:
        ctn = f.read().splitlines()
    return ctn


def _status_map():
    known_files = _known_files()
    res = _cmd('git status -s')
    smap = {}
    for line in res.splitlines():
        if line == '':
            continue
        key, file = _extract_status(line)
        if file in known_files:
            continue
        if key not in smap:
            smap[key] = []
        smap[key].append(file)
    return smap


def _process_gs_add(args):
    smap = _status_map()
    files = []
    for values in smap.values():
        files.extend(values)
    res = _cmd(f'git add {" ".join(files)}')
    print(res)


def _process_gs_gen_add(args):
    with open(KNOWN_FILES, 'a') as f:
        f.write(f'\n{args.file}')


def _process_gs_gen(args):
    gencmd_map = {
        'add': _process_gs_gen_add
    }
    if args.gencmd:
        gencmd_map[args.gencmd](args)
        return
    if os.path.exists(KNOWN_FILES):
        print(f'{KNOWN_FILES} already exists')
    with open(KNOWN_FILES, 'w') as f:
        f.write(KNOWN_FILES)


def _process_gs_diff(args):
    smap = _status_map()
    files = []
    for values in smap.values():
        files.extend(values)
    os.system(f'git diff {" ".join(files)}')


def process_gs(args):
    subcmd_map = {
        'add': _process_gs_add,
        'diff': _process_gs_diff,
        'gen': _process_gs_gen
    }
    if args.subcmd:
        subcmd_map[args.subcmd](args)
        return

    branch = _get_branch()
    ctn = []
    if not args.short:
        ctn.append(f'On Branch {branch}\n')
    smap = _status_map()
    for status in [NOT_ADDED, GIT_ADDED, UNTRACKED]:
        if status not in smap:
            continue
        if not args.short:
            ctn.append(f'{status}:')
        for file in smap[status]:
            prefix = '' if args.short else '\t'
            ctn.append(f'{prefix}{file}')
    print('\n'.join(ctn))


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


def process(args):
    cmd_map = {
        'gs': process_gs,
    }
    cmd_map[args.cmd](args)


def main():
    args = parse_args()
    process(args)


if __name__ == '__main__':
    main()
