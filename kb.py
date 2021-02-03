#!/usr/bin/python
from argparse import ArgumentParser
import os

# Known kubectl commands
KB_COMMANDS = ['pods', 'hpa', 'deployment', 'exec', 'edit']


class KubeGrammar:
    single_cmd = ['pods', 'hpa', 'cm', 'deployment', 'ingress', 'rq']
    pos_cmd = ['hpa', 'cm', 'deployment', 'ingress', 'rq']
    acc_cmd = ['describe', 'edit']
    all_cmd = single_cmd + pos_cmd + acc_cmd + ['exec', 'restart']

    def __init__(self, words):
        if len(words) < 2:
            raise Exception('Kube command should has at least 2 arguments')
        self.words = words
        self.service = words[0]
        self.cmd = words[1]
        self.args = words[2:]
        self._validate()

    def _validate(self):
        self._validate_service()
        self._validate_command()
        if self.cmd in self.acc_cmd:
            self._validate_pos_command()
        elif self.cmd == 'exec':
            self._validate_exec()
        elif self.cmd == 'restart':
            self._validate_restart()

    def _validate_command(self):
        if self.cmd not in self.all_cmd:
            raise Exception(f'Invalid command: {self.cmd}')

    def _validate_exec(self):
        if len(self.args) < 1:
            raise Exception(f'{self.cmd} require pod name')
        self.pod_name = self.args[0]
        self.args = self.args[1:]
        if self.pod_name == self.service or self.pod_name in self.all_cmd:
            raise Exception(f'Invalid pod name: {self.pod_name}')

    def _validate_pos_command(self):
        if len(self.args) < 1:
            raise Exception(
                f'{self.cmd} require at least 1 more arguments'
            )
        self.sub_cmd = self.args[0]
        self.args = self.args[1:]
        if self.sub_cmd not in self.pos_cmd:
            raise Exception(f'Invalid sub-command: {self.sub_cmd}')
        if len(self.args) >= 1:
            self.pod_name = self.args[0]
            self.args = self.args[1:]

    def _validate_restart(self):
        if len(self.args) < 1:
            raise Exception(
                f'{self.cmd} require at least 1 more arguments'
            )
        if len(self.args) >= 1:
            self.pod_name = self.args[0]
            self.args = self.args[1:]

    def _validate_service(self):
        if self.service in self.all_cmd:
            raise Exception(f'Invalid service name: {self.service}')


class KubeProcessor:
    def __init__(self, kg: KubeGrammar):
        self.kg = kg

    def process(self):
        if self.kg.cmd in KubeGrammar.single_cmd:
            cmd = self._process_get()
        elif self.kg.cmd in KubeGrammar.acc_cmd:
            cmd = self._process_acc()
        elif self.kg.cmd == 'exec':
            svc = self.kg.service
            pod = self.kg.pod_name
            if pod == 'auto':
                fpipe = (
                    "grep -Ei Running | grep -Eiv background | "
                    "head -1 | awk '{print $1}'"
                )
                pod = f'$(kubectl -n {svc} get pods | {fpipe})'
            cmd = f'kubectl -n {svc} exec -it {pod} -- sh'
        elif self.kg.cmd == 'restart':
            cmd = self._process_restart()
        else:
            cmd = ''
        os.system(cmd)

    def _process_acc(self):
        if self.kg.sub_cmd == 'rq':
            self.kg.sub_cmd = 'resourcequota'
        cmd = f'kubectl -n {self.kg.service} {self.kg.cmd} {self.kg.sub_cmd}'
        if self.kg.cmd == 'edit':
            cmd = f'KUBE_EDITOR=nano {cmd}'
        try:
            cmd = f'{cmd} {self.kg.pod_name}'
        except AttributeError:
            pass
        finally:
            return cmd

    def _process_get(self):
        if self.kg.cmd == 'rq':
            self.kg.cmd = 'resourcequota'
        cmd = f'kubectl -n {self.kg.service} get {self.kg.cmd}'
        if self.kg.args:
            fkey = self.kg.args[0]
            cmd = f'{cmd} | grep -Ei {fkey}'
        return cmd

    def _process_restart(self):
        cmd = (
            f'kubectl -n {self.kg.service} rollout restart '
            f'deployment/{self.kg.pod_name}'
        )
        return cmd


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
    try:
        kg = KubeGrammar(args.keywords)
        kp = KubeProcessor(kg)
        kp.process()
    except Exception as e:
        print(e)


def main():
    args = parse_args()
    process(args)


if __name__ == '__main__':
    main()
