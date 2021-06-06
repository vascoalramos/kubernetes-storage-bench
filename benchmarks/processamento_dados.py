
from pyquery import PyQuery as pq
from multiprocessing import Pool

import demjson
import pandas as pd
import matplotlib.pyplot as plt
import re

from parsing import *
from graphs import *


def make_graphs_for_scenario(app, storage, test_name, test_size):
    print(f'Making graphs for scenario {app} {storage} {test_name} {test_size}')

    make_system_graphs(app, storage, test_name, test_size)

    if storage == 'NFS':
        make_disk_nfs_graph(app, test_name, test_size)
    else:
        make_disk_ceph_graph(app, test_name, test_size)

    make_locust_graphs(app, storage, test_name, test_size)

    
def f(x):
    return make_graphs_for_scenario(*x)


def make_graphs():
    graphs = []

    for app in ['Wiki', 'NextCloud', 'PeerTube']:
        for storage in ['NFS', 'Ceph']:
            for test_name in ['staticRead', 'staticWrite', 'simulateUser']:
                for test_size in [25, 50, 75, 100]:
                    # Excepção: O PeerTube não tem testes acima de 25
                    if app == 'PeerTube' and test_size > 25:
                        continue
                    
                    # Excepção temporária: o Wiki ainda não tem Ceph, mas assim que tiver, basta remover isto
                    if app == 'Wiki' and storage == 'Ceph':
                        continue
                        
                    graphs.append((app, storage, test_name, test_size))

    with Pool(4) as p:
        p.map(f, graphs)


def main():
    make_graphs()


if __name__ == '__main__':
    main()
