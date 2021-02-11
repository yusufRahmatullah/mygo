from kb import BaseCmd, CmdFactory

test_cases = [
    # test simple get pods
    ['my-service pods', 'kubectl -n my-service get pods'],
    # test get pods with query
    ['my-service pods web', 'kubectl -n my-service get pods | grep -Ei web'],
    ['my-service pods background',
        'kubectl -n my-service get pods | grep -Ei background'],
    ['my-service pods auto', 'kubectl -n my-service get pods | grep -Ei auto'],
    # test get hpa
    ['my-service hpa', 'kubectl -n my-service get hpa'],
    ['my-service hpa web', 'kubectl -n my-service get hpa | grep -Ei web'],
    # test get cm
    ['my-service cm', 'kubectl -n my-service get cm'],
    ['my-service cm web', 'kubectl -n my-service get cm | grep -Ei web'],
    # test get deployment
    ['my-service deployment', 'kubectl -n my-service get deployment'],
    ['my-service deployment web', 'kubectl -n my-service get deployment | grep -Ei web'],
    # test get ingress
    ['my-service ingress', 'kubectl -n my-service get ingress'],
    ['my-service ingress web', 'kubectl -n my-service get ingress | grep -Ei web'],
    # test get reseource quota
    ['my-service rq', 'kubectl -n my-service get resourcequota'],
    ['my-service rq web', 'kubectl -n my-service get resourcequota | grep -Ei web'],
    # test describe
    ['my-service describe hpa', 'kubectl -n my-service describe hpa'],
    ['my-service describe cm', 'kubectl -n my-service describe cm'],
    ['my-service describe deployment', 'kubectl -n my-service describe deployment'],
    ['my-service describe ingress', 'kubectl -n my-service describe ingress'],
    ['my-service describe rq', 'kubectl -n my-service describe resourcequota'],
    ['my-service describe hpa my-pod', 'kubectl -n my-service describe hpa my-pod'],
    ['my-service describe cm my-pod', 'kubectl -n my-service describe cm my-pod'],
    ['my-service describe deployment my-pod',
        'kubectl -n my-service describe deployment my-pod'],
    ['my-service describe ingress my-pod',
        'kubectl -n my-service describe ingress my-pod'],
    ['my-service describe rq my-pod',
        'kubectl -n my-service describe resourcequota my-pod'],
    # test edit
    ['my-service edit hpa', 'KUBE_EDITOR=nano kubectl -n my-service edit hpa'],
    ['my-service edit cm', 'KUBE_EDITOR=nano kubectl -n my-service edit cm'],
    ['my-service edit deployment',
        'KUBE_EDITOR=nano kubectl -n my-service edit deployment'],
    ['my-service edit ingress', 'KUBE_EDITOR=nano kubectl -n my-service edit ingress'],
    ['my-service edit rq', 'KUBE_EDITOR=nano kubectl -n my-service edit resourcequota'],
    ['my-service edit hpa my-pod',
        'KUBE_EDITOR=nano kubectl -n my-service edit hpa my-pod'],
    ['my-service edit cm my-pod', 'KUBE_EDITOR=nano kubectl -n my-service edit cm my-pod'],
    ['my-service edit deployment my-pod',
        'KUBE_EDITOR=nano kubectl -n my-service edit deployment my-pod'],
    ['my-service edit ingress my-pod',
        'KUBE_EDITOR=nano kubectl -n my-service edit ingress my-pod'],
    ['my-service edit rq my-pod',
        'KUBE_EDITOR=nano kubectl -n my-service edit resourcequota my-pod'],
    # test exec
    ['my-service exec my-pod', 'kubectl -n my-service exec -it my-pod -- sh'],
    ['my-service exec auto',
        'kubectl -n my-service exec -it $(kubectl -n my-service get pods | grep -Ei Running | grep -Eiv background | head -1 | awk \'{print $1}\') -- sh'],
    # test restart
    ['my-service restart my-pod',
        'kubectl -n my-service rollout restart deployment/my-pod'],
    # test pf
    ['my-service pf 8080 my-pod', 'kubectl -n my-service port-forward my-pod 8080:8080'],
    ['my-service pf 8080 auto',
        'kubectl -n my-service port-forward $(kubectl -n my-service get pods | grep -Ei Running | grep -Eiv background | head -1 | awk \'{print $1}\') 8080:8080'],
]


def assert_cmd(keywords, expect):
    cmd_cls: BaseCmd
    cmd_cls = CmdFactory.get_cmd(keywords)
    cmd = cmd_cls.process()
    assert cmd == expect, f'expecy "{expect}", got "{cmd}"'


def test_all():
    for args, expect in test_cases:
        keywords = args.split()
        assert_cmd(keywords, expect)
        print('.', end='')
    print()
    n = len(test_cases)
    print(f'All {n} test cases are passed')


if __name__ == '__main__':
    test_all()
