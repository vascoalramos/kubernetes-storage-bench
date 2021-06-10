
from pyquery import PyQuery as pq
from multiprocessing import Pool

import demjson
import pandas as pd
import matplotlib.pyplot as plt
import re

from parsing import *
from graphs import *


def f(x):
    f, p = x

    print(f'Making graph for {" ".join([str(x) for x in p])}')

    return f(*p)


def make_graphs():
    graphs = []

    # for app in ['Wiki', 'NextCloud', 'PeerTube']:
    #     for storage in ['NFS', 'Ceph']:
    #         for test_name in ['staticRead', 'staticWrite', 'simulateUser']:
    #             for test_size in [25, 50, 75, 100]:
    #                 # Excepção: O PeerTube não tem testes acima de 25
    #                 if app == 'PeerTube' and test_size > 25:
    #                     continue
                    
    #                 # Excepção temporária: o Wiki ainda não tem Ceph num certo cenário, mas assim que tiver, basta remover isto
    #                 if app == 'Wiki' and storage == 'Ceph' and test_size >= 75 and test_name == 'simulateUser':
    #                     continue
                    
    #                 graphs.append((make_system_graphs, (app, storage, test_name, test_size)))
    #                 graphs.append((make_disk_nfs_graph, (app, test_name, test_size)) if storage == 'NFS' \
    #                     else (make_disk_ceph_graph, (app, test_name, test_size)))
    #                 graphs.append((make_locust_graphs, (app, storage, test_name, test_size)))

    graphs.append((make_disk_comparation_graph, ('NextCloud', 'staticWrite', 100)))
    graphs.append((make_disk_comparation_graph, ('Wiki', 'staticWrite', 100)))

    with Pool(4) as p:
        p.map(f, graphs)


def main():
    make_graphs()


if __name__ == '__main__':
    main()
