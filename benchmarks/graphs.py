from parsing import *

import matplotlib.pyplot as plt
import os


def make_graph(app, storage, test_name, test_size, dfs, y_axis_label, graph_type, \
    x_axis_label = 'Tempo desde início do benchmark (HH:MM:SS)', rotate_xlabel = True, close = True):
    fig, ax = plt.subplots(figsize = (16, 10))

    if type(dfs) == list:
        for df in dfs:
            df.plot(ax = ax, legend = len(dfs) > 1)
    elif callable(dfs):
        dfs(ax)

    ax.set_xlabel(x_axis_label, fontdict={'fontsize':12})
    ax.set_ylabel(y_axis_label, fontdict={'fontsize':12})

    if rotate_xlabel:
        ax.tick_params(axis = 'x', labelrotation = 45)

    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_fontsize(14)
        tick.label1

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(14)
        tick.label1

    filepath = f'{app.lower()}/{storage.replace("/", "_").lower()}/{test_name}_{test_size}'
    os.makedirs(filepath, exist_ok = True)
    fig.savefig(f'{filepath}/{test_name}_{test_size}_{graph_type}.png', transparent = True, bbox_inches = 'tight')

    if close:
        plt.close(fig)
    else:
        plt.show()


def make_system_graphs(app, storage, test_name, test_size, close = True):
    df = read_dfs_system(app, storage, test_name, test_size)[['cpu_%', 'mem_%', 'net_recv_mb', 'net_send_mb']]

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
        y_axis_label = 'Utilização do CPU (%)',
        graph_type = 'cpu',
        close = close
    )

    make_graph(app, storage, test_name, test_size,
        [mem_usage],
        y_axis_label = 'Utilização da RAM (%)',
        graph_type = 'mem',
        close = close
    )

    usage_net_recv = df.reset_index() \
        .pivot(index = 'time', columns = 'machine', values = ['net_recv_mb'])['net_recv_mb'] \
        .sum(axis = 1) \
        .rolling(2).mean() \
        .dropna()
    usage_net_recv.name = 'Network RX'
    
    usage_net_send = df.reset_index() \
        .pivot(index = 'time', columns = 'machine', values = ['net_send_mb'])['net_send_mb'] \
        .sum(axis = 1) \
        .rolling(2).mean() \
        .dropna()
    usage_net_send.name = 'Network TX'

    make_graph(app, storage, test_name, test_size,
        [usage_net_recv, usage_net_send],
        y_axis_label = 'Utilização da rede (Mb/s)',
        graph_type = 'net',
        close = close
    )


def make_disk_nfs_graph(app, test_name, test_size, close = True):
    df = read_df_io(app, 'nfs', test_name, test_size, 'cloud108').loc['cloud108']

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
        y_axis_label = 'Utilização do disco (MB/s)',
        graph_type = 'disk',
        close = close
    )


def make_disk_ceph_graph(app, test_name, test_size, close = True):
    df = read_dfs_io(app, 'ceph', test_name, test_size)

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
        y_axis_label = 'Utilização do disco (MB/s)',
        graph_type = 'disk',
        close = close
    )


def make_disk_comparation_graph(app, test_name, test_size, close = True, type = 'write'):
    df_nfs = read_df_io(app, 'nfs', test_name, test_size, 'cloud108').loc['cloud108']
    df_ceph = read_dfs_io(app, 'ceph', test_name, test_size)

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
        y_axis_label = 'Utilização do disco (MB/s)',
        graph_type = 'disk',
        close = close
    )


def make_locust_report_graphs(app, storage, test_name, test_size, close = True):
    df = read_df_reporthtml(app, storage, test_name, test_size)[['current_rps', 'current_fail_per_sec', 'response_time_percentile_50']]

    rps_series = df['current_rps'].rolling(2).mean().dropna()
    rps_series.name = 'Pedidos por segundo'
    
    fps_series = df['current_fail_per_sec'].rolling(2).mean().dropna()
    fps_series.name = 'Falhas por segundo'

    responsetimes_series = df['response_time_percentile_50'].rolling(2).mean().dropna()

    make_graph(app, storage, test_name, test_size,
        [rps_series, fps_series],
        y_axis_label = 'Nº de pedidos/s',
        graph_type = 'rpsfps',
        close = close
    )

    make_graph(app, storage, test_name, test_size,
        [responsetimes_series],
        y_axis_label = 'Tempo de resposta (ms)',
        graph_type = 'responsetimes',
        close = close
    )


def make_locust_csv_graphs(app, storage, test_name, close = True):
    df = read_df_locustcsv(app, storage, test_name)

    def draw(ax):
        df.plot(ax = ax, marker = 'o')
    
    make_graph(app, storage, test_name, 'all',
        draw,
        x_axis_label = 'Tempo de resposta (s)',
        y_axis_label = 'Nº de pedidos/s',
        graph_type = 'rps_of_responsetimes',
        close = close,
        rotate_xlabel = False
    )


def make_reqfails_comparation_graph(app, test_name, test_size, close = True):
    df_nfs = read_df_reporthtml(app, 'NFS', test_name, test_size)[['current_rps', 'current_fail_per_sec']]
    df_ceph = read_df_reporthtml(app, 'Ceph', test_name, test_size)[['current_rps', 'current_fail_per_sec']]

    rps_series_nfs = df_nfs['current_rps'] # .rolling(2).mean().dropna()
    rps_series_nfs.name = 'NFS'
    # rps_series_nfs.name = 'Pedidos por segundo (NFS)'
    
    # fps_series_nfs = df_nfs['current_fail_per_sec'] # .rolling(2).mean().dropna()
    # fps_series_nfs.name = 'Falhas por segundo (NFS)'

    rps_series_ceph = df_ceph['current_rps'] # .rolling(2).mean().dropna()
    rps_series_ceph.name = 'Ceph'
    # rps_series_ceph.name = 'Pedidos por segundo (Ceph)'
    
    # fps_series_ceph = df_ceph['current_fail_per_sec'] # .rolling(2).mean().dropna()
    # fps_series_ceph.name = 'Falhas por segundo (Ceph)'

    def draw(ax):
        rps_series_nfs.plot(ax = ax, linestyle = '-', color = 'blue', legend = True)
        # fps_series_nfs.plot(ax = ax, linestyle = '-', color = 'blue', legend = True)

        rps_series_ceph.plot(ax = ax, linestyle = '-', color = 'red', legend = True)
        # fps_series_ceph.plot(ax = ax, linestyle = '-', color = 'red', legend = True)

    make_graph(app, 'NFS/Ceph', test_name, test_size,
        draw,
        y_axis_label = 'Nº de pedidos/s',
        graph_type = 'rpsfps',
        close = close
    )


def make_responsetimes_comparation_graph(app, test_name, test_size, close = True):
    df_nfs = read_df_reporthtml(app, 'NFS', test_name, test_size)[['response_time_percentile_50']]
    df_ceph = read_df_reporthtml(app, 'Ceph', test_name, test_size)[['response_time_percentile_50']]

    responsetimes_series_nfs = df_nfs['response_time_percentile_50']
    responsetimes_series_nfs.name = 'NFS'

    responsetimes_series_ceph = df_ceph['response_time_percentile_50']
    responsetimes_series_ceph.name = 'Ceph'

    def draw(ax):
        responsetimes_series_nfs.plot(ax = ax, linestyle = '-', color = 'blue', legend = True)
        responsetimes_series_ceph.plot(ax = ax, linestyle = '-', color = 'red', legend = True)
    
    make_graph(app, 'NFS/Ceph', test_name, test_size,
        draw,
        y_axis_label = 'Tempo de resposta (ms)',
        graph_type = 'responsetimes',
        close = close
    )
