from parsing import *

import matplotlib.pyplot as plt
import os


def make_graph(app, storage, test_name, test_size, dfs, title, y_axis_label, graph_type, close = True):
    fig, ax = plt.subplots(figsize = (16, 10))

    for df in dfs:
        df.plot(
            ax = ax,
            legend = len(dfs) > 1
        )

    ax.set_title(title)

    ax.set_xlabel('Tempo desde início do benchmark (HH:MM:SS)')
    ax.set_ylabel(y_axis_label)

    ax.tick_params(axis = 'x', labelrotation = 45)

    filepath = f'{app.lower()}/{storage.replace("/", "_").lower()}/{test_name}_{test_size}'
    os.makedirs(filepath, exist_ok = True)
    fig.savefig(f'{filepath}/{test_name}_{test_size}_{graph_type}.png')

    if close:
        plt.close(fig)
    else:
        plt.show()


def make_system_graphs(app, storage, test_name, test_size, close = True):
    df = read_dfs_system(app, storage, test_name, test_size)[['cpu_%', 'mem_%', 'net_recv_kb', 'net_send_kb']]

    test_name_simple = test_name.replace('static', '').lower()

    cpu_usage = df.reset_index() \
        .pivot(index = 'time', columns = 'machine', values = ['cpu_%'])['cpu_%'] \
        .median(axis = 1) \
        .rolling(2).mean() \
        .dropna()
    
    mem_usage = df.reset_index() \
        .pivot(index = 'time', columns = 'machine', values = ['mem_%'])['mem_%'] \
        .median(axis = 1) \
        .rolling(2).mean() \
        .dropna()

    make_graph(app, storage, test_name, test_size,
        [cpu_usage],
        title = f'Utilização mediana do CPU pelas três máquinas durante o benchmarking do {app} (rolling avg. 10s, teste de {test_name_simple}, backend {storage}, {test_size} utilizadores)',
        y_axis_label = 'Utilização do CPU (%)',
        graph_type = 'cpu',
        close = close
    )

    make_graph(app, storage, test_name, test_size,
        [mem_usage],
        title = f'Utilização mediana da RAM pelas três máquinas durante o benchmarking do {app} (rolling avg. 10s, teste de {test_name_simple}, backend {storage}, {test_size} utilizadores)',
        y_axis_label = 'Utilização da RAM (%)',
        graph_type = 'mem',
        close = close
    )

    usage_net_recv = df.reset_index() \
        .pivot(index = 'time', columns = 'machine', values = ['net_recv_kb'])['net_recv_kb'] \
        .sum(axis = 1) \
        .rolling(2).mean() \
        .dropna()
    usage_net_recv.name = 'Network RX'
    
    usage_net_send = df.reset_index() \
        .pivot(index = 'time', columns = 'machine', values = ['net_send_kb'])['net_send_kb'] \
        .sum(axis = 1) \
        .rolling(2).mean() \
        .dropna()
    usage_net_send.name = 'Network TX'

    make_graph(app, storage, test_name, test_size,
        [usage_net_recv, usage_net_send],
        title = f'Utilização total da rede pelas três máquinas durante o benchmarking do {app} (rolling avg. 10s, teste de {test_name_simple}, backend {storage}, {test_size} utilizadores)',
        y_axis_label = 'Utilização da rede (Kb/s)',
        graph_type = 'net',
        close = close
    )


def make_disk_nfs_graph(app, test_name, test_size, close = True):
    df = read_df_io(app, 'nfs', test_name, test_size, 'cloud108').loc['cloud108']

    test_name_simple = test_name.replace('static', '').lower()

    read_series = df['read_mb'] \
        .rolling(2).mean() \
        .dropna()
    read_series.name = 'Leitura'

    write_series = df['write_mb'] \
        .rolling(2).mean() \
        .dropna()
    write_series.name = 'Escrita'

    make_graph(app, 'NFS', test_name, test_size,
        [read_series, write_series],
        title = f'Utilização do disco durante o benchmarking do {app} (rolling avg. 10s, teste de {test_name_simple}, backend NFS, {test_size} utilizadores)',
        y_axis_label = 'Utilização do disco (MB/s)',
        graph_type = 'disk',
        close = close
    )


def make_disk_ceph_graph(app, test_name, test_size, close = True):
    df = read_dfs_io(app, 'ceph', test_name, test_size)

    test_name_simple = test_name.replace('static', '').lower()

    read_series = df.reset_index() \
        .pivot(index = 'time', columns = 'machine', values = ['read_mb'])['read_mb'] \
        .sum(axis = 1) \
        .rolling(2).mean() \
        .dropna()
    read_series.name = 'Leitura'

    write_series = df.reset_index() \
        .pivot(index = 'time', columns = 'machine', values = ['write_mb'])['write_mb'] \
        .sum(axis = 1) \
        .rolling(2).mean() \
        .dropna()
    write_series.name = 'Escrita'

    make_graph(app, 'Ceph', test_name, test_size,
        [read_series, write_series],
        title = f'Utilização do disco total nas três máquinas durante o benchmarking do {app} (rolling avg. 10s, teste de {test_name_simple}, backend Ceph, {test_size} utilizadores)',
        y_axis_label = 'Utilização do disco (MB/s)',
        graph_type = 'disk',
        close = close
    )


def make_disk_comparation_graph(app, test_name, test_size, close = True, type = 'write'):
    df_nfs = read_df_io(app, 'nfs', test_name, test_size, 'cloud108').loc['cloud108']
    df_ceph = read_dfs_io(app, 'ceph', test_name, test_size)

    test_name_simple = test_name.replace('static', '').lower()

    series_nfs = df_nfs[type + '_mb'] \
        .rolling(2).mean() \
        .dropna()
    series_nfs.name = 'Leitura NFS' if type == 'read' else 'Escrita NFS'

    series_ceph = df_ceph.reset_index() \
        .pivot(index = 'time', columns = 'machine', values = [type + '_mb'])[type + '_mb'] \
        .sum(axis = 1) \
        .rolling(2).mean() \
        .dropna()
    series_ceph.name = 'Leitura Ceph' if type == 'read' else 'Escrita Ceph'

    make_graph(app, 'NFS/Ceph', test_name, test_size,
        [series_nfs, series_ceph],
        title = f'Comparação da utilização total dos discos entre NFS e Ceph durante o benchmarking do {app} (rolling avg. 10s, teste de {test_name_simple}, {test_size} utilizadores)',
        y_axis_label = 'Utilização do disco (MB/s)',
        graph_type = 'disk',
        close = close
    )


def make_locust_graphs(app, storage, test_name, test_size, close = True):
    df = read_df_reporthtml(app, storage, test_name, test_size)[['current_rps', 'current_fail_per_sec', 'response_time_percentile_50']]

    test_name_simple = test_name.replace('static', '').lower()

    rps_series = df['current_rps'].rolling(2).mean().dropna()
    rps_series.name = 'Pedidos por segundo'
    
    fps_series = df['current_fail_per_sec'].rolling(2).mean().dropna()
    fps_series.name = 'Falhas por segundo'

    responsetimes_series = df['response_time_percentile_50'].rolling(2).mean().dropna()
    
    make_graph(app, storage, test_name, test_size,
        [rps_series, fps_series],
        title = f'Taxa de pedidos e falhas por segundo médios obtidos durante o benchmarking do {app} (rolling avg. 10s, teste de {test_name_simple}, backend {storage}, {test_size} utilizadores)',
        y_axis_label = 'Nº de pedidos/s',
        graph_type = 'rpsfps',
        close = close
    )

    make_graph(app, storage, test_name, test_size,
        [responsetimes_series],
        title = f'Tempos de resposta medianos obtidos durante o benchmarking do {app} (rolling avg. 10s, teste de {test_name_simple}, backend {storage}, {test_size} utilizadores)',
        y_axis_label = 'Tempo de resposta (ms)',
        graph_type = 'responsetimes',
        close = close
    )
