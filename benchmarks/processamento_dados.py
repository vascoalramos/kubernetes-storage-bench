
from multiprocessing import Pool

from parsing import *
from graphs import *

from datetime import datetime


def f(x):
    f, p = x

    print(f'Making graph for {" ".join([str(x) for x in p])}')

    return f(*p)


def make_graphs():
    graphs = []

    for app in ['Wiki', 'NextCloud', 'PeerTube']:
        for storage in ['NFS', 'Ceph']:
            for test_name in ['staticRead', 'staticWrite', 'simulateUser']:
                for test_size in [25, 50, 75, 100]:
                    # Excepção: O PeerTube não tem testes acima de 25
                    if app == 'PeerTube' and test_size > 25:
                        continue
                    
                    graphs.append((make_system_graphs, (app, storage, test_name, test_size)))
                    graphs.append((make_disk_nfs_graph, (app, test_name, test_size)) if storage == 'NFS' \
                        else (make_disk_ceph_graph, (app, test_name, test_size)))
                    graphs.append((make_locust_report_graphs, (app, storage, test_name, test_size)))

                if test_name == 'staticWrite' and app != 'PeerTube': # O PeerTube é tão mau, tão mau, que como não tem test_size > 25, dá asneira aqui
                    graphs.append((make_locust_csv_graphs, (app, storage, test_name)))

    for app in ['Wiki', 'NextCloud']:
        for test_size  in [25, 50, 75, 100]:
            graphs.append((make_reqfails_comparation_graph, (app, 'staticRead', test_size)))
            graphs.append((make_reqfails_comparation_graph, (app, 'simulateUser', test_size)))

            graphs.append((make_responsetimes_comparation_graph, (app, 'staticRead', test_size)))
            graphs.append((make_responsetimes_comparation_graph, (app, 'simulateUser', test_size)))

            graphs.append((make_disk_comparation_graph, (app, 'staticWrite', test_size)))

    with Pool(4) as p:
        p.map(f, graphs)


def main():
    t0 = datetime.now()
    make_graphs()
    t1 = datetime.now()

    diff = t1 - t0

    print()
    print(f'Built all graphs in {diff}ms')


if __name__ == '__main__':
    main()
