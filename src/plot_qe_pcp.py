import numpy as np
import matplotlib.pyplot as plt
import csv
from matplotlib.lines import Line2D
import os


def diff_between_dates_in_sec(s1, s2):
    from datetime import datetime

    fmt = "%a %b %d %H:%M:%S"
    d1 = datetime.strptime(s1, fmt)
    d2 = datetime.strptime(s2, fmt)
    diff = d1 - d2
    return (diff.seconds // 60)


def replace_qm_with_None(v):
    if v == '?':
        return None
    if 'G' in v:
        n = int(v.replace("G", "").replace(".", ""))
        return n * 1000000000
    if 'K' in v:
        n = int(v.replace("K", "").replace(".", ""))
        return n * 1000
    if 'M' in v:
        n = int(v.replace("M", "").replace(".", ""))
        return n * 1000000
    return v


def generate_graph(qs, mea_time, y_label, target_file, labels):
    fig, ax1 = plt.subplots()

    color = ['b', 'r', 'y', 'm']
    marker = ['s', 'o', 'v', 'x']

    idx = 0
    ps = []
    for q in qs:
        p, = ax1.plot(mea_time, q, 'b-', color=color[idx], marker=marker[idx], label=labels[idx])
        ps.append(p)
        idx = idx + 1

    ax1.set_xlabel('time (minutes)')
    ax1.set_ylabel(y_label, color='b')

    plt.legend()
    plt.savefig(target_file)


def plot(data_file, fields, labels, plot_file_prefix="qe_experiments_29_"):

    qe1 = {}
    qe2 = {}
    qe3 = {}
    qe4 = {}

    qes = [qe1, qe2, qe3, qe4]
    i = 0
    for q in qes:
        for f in fields:
            q[f] = []
        q["label"] = labels[i]
        i = i + 1

    mea_time = []

    first_data = None

    line_number = 0
    with open(data_file, 'rU') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in reader:
            if line_number > 1:
                col_num = 0
                if first_data is None:
                    first_data = row[col_num].strip()

                mea_time.append(diff_between_dates_in_sec(row[col_num].strip(), first_data))
                col_num = col_num + 1

                for q in qes:
                    for f in fields:
                        v = replace_qm_with_None(row[col_num].strip())
                        q[f].append(v)
                        col_num = col_num + 1
            line_number = line_number + 1

    for f in fields:
        meas = [q[f] for q in qes]
        y_label = "{0}".format(f)
        result_picture = "{0}_{1}.jpeg".format(plot_file_prefix, f)
        result_picture = result_picture.replace(" ", "_")
        generate_graph(meas, mea_time, y_label, result_picture, labels)


def get_data_for_mem_and_cpu(pcp_data_dir, result_file_prefix, from_time, till_time):

    my_dir = os.path.dirname(os.path.realpath(__file__))

    result_file = "{0}_mem_load.txt".format(result_file_prefix)

    os.system("rm -f {0}/{1}".format(my_dir, result_file))

    os.system("""
cd {0} ; pmdumptext  -t 30sec -i -l -S @'{3}' -T @'{4}' \
"leads-qe2:kernel.all.load[1]" "leads-qe2:mem.util.used" \
"leads-qe5:kernel.all.load[1]" "leads-qe5:mem.util.used" \
"leads-qe3:kernel.all.load[1]" "leads-qe3:mem.util.used" \
"leads-qe4:kernel.all.load[1]" "leads-qe4:mem.util.used" \
    -a leads-qe2/20150430.00.10.0,leads-qe5/20150430.00.10.0,\
leads-qe3/20150430.00.10.0,leads-qe4/20150430.11.29.0 > {1}/{2}
    """.format(pcp_data_dir, my_dir, result_file, from_time, till_time))

    return result_file


def get_data_for_network_in_out_bytes(pcp_data_dir, result_file_prefix, from_time, till_time):
    my_dir = os.path.dirname(os.path.realpath(__file__))

    result_file = "{0}_network_in_out.txt".format(result_file_prefix)

    os.system("rm -f {0}/{1}".format(my_dir, result_file))

    os.system("""
cd {0} ; pmdumptext  -t 30sec -i -l -S @'{3}' -T @'{4}' \
    'leads-qe2:network.interface.in.bytes' 'leads-qe2:network.interface.out.bytes'\
    'leads-qe5:network.interface.in.bytes' 'leads-qe5:network.interface.out.bytes'\
    'leads-qe3:network.interface.in.bytes' 'leads-qe3:network.interface.out.bytes'\
    'leads-qe4:network.interface.in.bytes' 'leads-qe4:network.interface.out.bytes'\
    -a leads-qe2/20150430.00.10.0,leads-qe5/20150430.00.10.0,\
leads-qe3/20150430.00.10.0,leads-qe4/20150430.11.29.0 > {1}/{2}
    """.format(pcp_data_dir, my_dir, result_file, from_time, till_time))

    return result_file


def get_data_for_disk_read_write_bytes(pcp_data_dir, result_file_prefix, from_time, till_time):
    my_dir = os.path.dirname(os.path.realpath(__file__))

    result_file = "{0}_disk_write_read.txt".format(result_file_prefix)

    os.system("rm -f {0}/{1}".format(my_dir, result_file))

    os.system("""
cd {0} ; pmdumptext  -t 30sec -i -l -S @'{3}' -T @'{4}' \
   "leads-qe2:disk.all.write_bytes" "leads-qe2:disk.all.read_bytes"\
    "leads-qe5:disk.all.write_bytes" "leads-qe5:disk.all.read_bytes"\
    "leads-qe3:disk.all.write_bytes" "leads-qe3:disk.all.read_bytes"\
    "leads-qe4:disk.all.write_bytes" "leads-qe4:disk.all.read_bytes"\
    -a leads-qe2/20150430.00.10.0,leads-qe5/20150430.00.10.0,\
leads-qe3/20150430.00.10.0,leads-qe4/20150430.11.29.0 > {1}/{2}
    """.format(pcp_data_dir, my_dir, result_file, from_time, till_time))

    return result_file


def plot_q1(pcp_data_dir, result_file_prefix, labels):
    result_file = get_data_for_mem_and_cpu(pcp_data_dir, result_file_prefix,
                                           "2015-04-30 17:35",
                                           "2015-04-30 18:05")
    plot(result_file, ["kernel load", "memory used"], labels, result_file_prefix)

    result_file = get_data_for_network_in_out_bytes(pcp_data_dir, result_file_prefix,
                                                    "2015-04-30 17:35",
                                                    "2015-04-30 18:05")
    plot(result_file, ["network received bytes", "network sent bytes"], labels, result_file_prefix)

    result_file = get_data_for_disk_read_write_bytes(pcp_data_dir, result_file_prefix,
                                                     "2015-04-30 17:35",
                                                     "2015-04-30 18:05")
    plot(result_file, ["write bytes to disk", "read bytes from disk"], labels, result_file_prefix)


def plot_q2(pcp_data_dir, result_file_prefix, labels):

    result_file = get_data_for_mem_and_cpu(pcp_data_dir, result_file_prefix,
                                           "2015-04-30 18:05",
                                           "2015-04-30 18:25")
    plot(result_file, ["kernel load", "memory used"], labels, result_file_prefix)

    result_file = get_data_for_network_in_out_bytes(pcp_data_dir, result_file_prefix,
                                                    "2015-04-30 18:05",
                                                    "2015-04-30 18:25")
    plot(result_file, ["network received bytes", "network sent bytes"], labels, result_file_prefix)

    result_file = get_data_for_disk_read_write_bytes(pcp_data_dir, result_file_prefix,
                                                     "2015-04-30 18:05",
                                                     "2015-04-30 18:25")
    plot(result_file, ["write bytes to disk", "read bytes from disk"], labels, result_file_prefix)


if __name__ == "__main__":

    pcp_data_dir = os.environ["LEADS_PCP_REPORT_DIR"]
    result_file_prefix_q1 = "qe_experiments_q1"
    result_file_prefix_q2 = "qe_experiments_q2"

    labels = ["qe2", "qe5", "qe3", "qe2"]

    plot_q1(pcp_data_dir, result_file_prefix_q1, labels)
    plot_q2(pcp_data_dir, result_file_prefix_q2, labels)
