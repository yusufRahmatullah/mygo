#!/usr/bin/python
from argparse import ArgumentParser
import os

# kubectl prefix
KB_PREFIX = 'kubectl -n'

# Known kubectl commands
KB_ALIAS = {
    'rq': 'resourcequota'
}
KB_COMMANDS = [
    'cm', 'deployment', 'hpa', 'ingress', 'pods', 'rq',
    'describe', 'edit',
    'exec', 'pf', 'restart',
]
KB_SUB_COMMANDS = ['cm', 'deployment', 'hpa', 'ingress', 'rq']


class BaseCmd:
    def __init__(self, keywords: list):
        self._parse_token(keywords)
        self._validate_service()
        self._validate_command()
        self._parse_alias()
        self.validate()
        self.parse_options()
        self.validate_options()

    def _parse_alias(self):
        self.cmd = KB_ALIAS.get(self.cmd, self.cmd)

    def _parse_token(self, keywords: list):
        self.service = keywords[0]
        self.cmd = keywords[1]
        self.args = keywords[2:]

    def _validate_command(self):
        if self.cmd not in KB_COMMANDS:
            raise Exception(f'Invalid command: {self.cmd}')

    def _validate_service(self):
        if self.service in KB_COMMANDS:
            raise Exception(f'Invalid service name: {self.service}')

    def parse_options(self):
        pass

    def process(self):
        print('process not implemented in', self.cmd)
        raise NotImplementedError

    def validate(self):
        print('validate not implemented in', self.cmd)
        raise NotImplementedError

    def validate_options(self):
        pass


class ExecCmd(BaseCmd):
    def parse_options(self):
        self.pod_name = self.args[0]
        self.args = self.args[1:]

    def process(self):
        svc = self.service
        pod = self.pod_name
        if pod == 'auto':
            fpipe = (
                "grep -Ei Running | grep -Eiv background | "
                "head -1 | awk '{print $1}'"
            )
            pod = f'$(kubectl -n {svc} get pods | {fpipe})'
        return f'kubectl -n {svc} exec -it {pod} -- sh'

    def validate(self):
        if len(self.args) < 1:
            raise Exception(f'{self.cmd} require pod name')

    def validate_options(self):
        if self.pod_name == self.service or self.pod_name in KB_COMMANDS:
            raise Exception(f'Invalid pod name: {self.pod_name}')


class GetCmd(BaseCmd):
    def process(self):
        pod_name = self.args[0] if self.args else ''
        cmd = f'{KB_PREFIX} {self.service} get {self.cmd}'
        if pod_name:
            cmd = f'{cmd} | grep -Ei {pod_name}'
        return cmd

    def validate(self):
        pass


class HasSubCmd(BaseCmd):
    def parse_options(self):
        self.sub_cmd = self.args[0]
        self.args = self.args[1:]
        if len(self.args) >= 1:
            self.pod_name = self.args[0]
            self.args = self.args[1:]

    def process(self):
        self.sub_cmd = KB_ALIAS.get(self.sub_cmd, self.sub_cmd)
        cmd = f'{KB_PREFIX} {self.service} {self.cmd} {self.sub_cmd}'
        if hasattr(self, 'pod_name'):
            cmd = f'{cmd} {self.pod_name}'
        return cmd

    def validate(self):
        if len(self.args) < 1:
            raise Exception(f'{self.cmd} require at least 1 more arguments')

    def validate_options(self):
        if self.sub_cmd not in KB_SUB_COMMANDS:
            raise Exception(f'Invalid sub-command: {self.sub_cmd}')


class RestartCmd(BaseCmd):
    def parse_options(self):
        if len(self.args) >= 1:
            self.pod_name = self.args[0]
            self.args = self.args[1:]

    def process(self):
        cmd = (
            f'kubectl -n {self.service} rollout restart '
            f'deployment/{self.pod_name}'
        )
        return cmd

    def validate(self):
        if len(self.args) < 1:
            raise Exception(
                f'{self.cmd} require at least 1 more arguments'
            )


class PortForwardCmd(BaseCmd):
    def parse_options(self):
        self.sub_cmd = self.args[0]
        self.args = self.args[1:]
        if len(self.args) >= 1:
            self.pod_name = self.args[0]
            self.args = self.args[1:]

    def process(self):
        svc = self.service
        pod = self.pod_name
        port = int(self.sub_cmd)
        if pod == 'auto':
            fpipe = (
                "grep -Ei Running | grep -Eiv background | "
                "head -1 | awk '{print $1}'"
            )
            pod = f'$(kubectl -n {svc} get pods | {fpipe})'
        print('\n============================================')
        print('Port Forwarding. Ensure to use right context')
        print('============================================\n')
        return f'kubectl -n {svc} port-forward {pod} {port}:{port}'

    def validate(self):
        if len(self.args) < 1:
            raise Exception(
                f'{self.cmd} require at least 1 more arguments'
            )


class EditCmd(HasSubCmd):
    def process(self):
        cmd = super().process()
        return f'KUBE_EDITOR=nano {cmd}'


class CmdFactory:
    _cmd_map = {
        'cm': GetCmd,
        'deployment': GetCmd,
        'hpa': GetCmd,
        'ingress': GetCmd,
        'pods': GetCmd,
        'rq': GetCmd,
        'describe': HasSubCmd,
        'edit': EditCmd,
        'exec': ExecCmd,
        'restart': RestartCmd,
        'pf': PortForwardCmd,
    }

    @classmethod
    def get_cmd(cls, keywords: str):
        cmd = keywords[1]
        cmd_cls = cls._cmd_map.get(cmd, BaseCmd)
        return cmd_cls(keywords)


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


def process(args):
    cmd_cls: BaseCmd
    cmd_cls = CmdFactory.get_cmd(args.keywords)
    cmd = cmd_cls.process()
    os.system(cmd)


def main():
    args = parse_args()
    process(args)


if __name__ == '__main__':
    main()
