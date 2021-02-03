#!/usr/bin/python
from argparse import ArgumentParser

import requests as req

BGP_IP_URL = 'https://api.bgpview.io/ip/{ip}'


def get_ip_info(ip):
    resp = req.get(BGP_IP_URL.format(ip=ip))
    return resp.json()


def format_prefix(prefix, full=False):
    sout = []
    pref = prefix.get('prefix', '')
    if not pref:
        return sout

    if full:
        sout.append(f'Prefix: {pref}')

    asn = prefix.get('asn', {})
    if not asn:
        return sout

    asn_no = asn.get('asn', '')
    name = asn.get('name', '')
    desc = asn.get('description', '')
    country = asn.get('country_code', '')
    sout.append(f'{asn_no} | {name} | {country} | {desc}')

    return sout


def format_output(output, ip, full=False):
    sout = []

    if full:
        status = output.get('status', 'failed')
        sout.append(f'Status: {status}')

    data = output.get('data', {})
    if not data:
        return sout

    if full:
        ip = data.get('ip', ip)
        sout.append(f'IP: {ip}')

    prefixes = data.get('prefixes', {})
    if not prefixes:
        return sout

    for pref in prefixes:
        fmt_pref = format_prefix(pref, full=full)
        if pref:
            if full:
                sout.append('\n')
            sout.extend(fmt_pref)
        if not full:
            break
    return sout


def parse_args():
    try:
        parser = ArgumentParser(description='IP ASN Information')
        parser.add_argument('ip', help='IP Address')
        parser.add_argument(
            '-f', '--full', action='store_true',
            help='Full output'
        )
        return parser.parse_args()
    except Exception:
        parser.print_help()
        exit(1)


def main():
    args = parse_args()
    ip_info = get_ip_info(args.ip)
    fmt_info = format_output(ip_info, args.ip, full=args.full)
    print('\n'.join(fmt_info))


if __name__ == '__main__':
    main()
