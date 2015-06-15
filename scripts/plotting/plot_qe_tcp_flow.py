from lxml import etree
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import sys
import os


def append_to_report(report_rows, key, mea):
    """
    """
    if key in report_rows:
        d = report_rows[key]
        d[2] = int(d[2]) + int(mea[2])
        d[3] = int(d[3]) + int(mea[3])
    else:
        report_rows[key] = mea


def get_data_for_viz(report_xml):

    with open(report_xml, 'r') as f:
        tree = etree.parse(f)

        f_objects = tree.xpath('/dfxml/configuration/fileobject')

        report_rows = {}

        for fo in f_objects:
            src_ipn = fo.xpath('tcpflow/@src_ipn')
            dst_ipn = fo.xpath('tcpflow/@dst_ipn')
            time_point = fo.xpath('tcpflow/@startime')
            file_size = fo.xpath('filesize/text()')[0]
            num_packets = fo.xpath('tcpflow/@packets')[0]
            report_key = src_ipn[0] + " -> " + dst_ipn[0]
            append_to_report(report_rows, report_key,
                             [src_ipn, dst_ipn, file_size, num_packets])
        return report_rows


def plot_ip_to_package_and_size(viz_data, x_data, y1_data, y2_data, label):
    fig, ax1 = plt.subplots(figsize=(12, 10))

    plt.subplots_adjust(bottom=0.30)
    plt.xticks(list(range(len(x_data))), x_data, rotation=90)

    # http://mainatplotlib.org/examples/api/two_scales.html
    ax1.set_xlabel('src -> target')
    ax1.set_ylabel('Number of packets', color='r')

    ax1.plot(y1_data, 'r.', marker='o', color='r', markersize=23)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Transmitted data size', color='b')

    ax2.plot(y2_data, 'm.', marker='v', color='b', markersize=24)

    plt.savefig("qe_experiments_30/q2/qe_experiments_tcp_flow_{0}.png".format(label))


def main():

    # LEADS_TCPFLOW_REPORT_DIR
    #    |-tcp-leads-qe1-query-2/report.xml
    #    |-tcp-leads-qe2-query-2/report.xml
    #    |-tcp-leads-qe2-query-2//report.xml
    #
    # where qe1 - qe4 - leads Query engine instances
    tcpflow_data_dir = os.environ["LEADS_TCPFLOW_REPORT_DIR"]
    experiment_name = os.getenv("LEADS_EXPERIMENT_NAME", "query-2")

    print "NOTICE: it only analyses closed tcp. TODO: process cap files"
    qes = ["qe2", "qe5", "qe3", "qe4"]

    for q in qes:
        file_path = "{0}/tcpflow-leads-{1}-{2}/report.xml".format(tcpflow_data_dir, q,
                                                                  experiment_name)
        print "Processing {0}".format(file_path)
        viz_data = get_data_for_viz(file_path)

        ip_src_dst = viz_data.keys()
        sizes = []
        num_of_packages = []
        x_dim = []
        for k in ip_src_dst:
            s = int(viz_data[k][2])
            n = int(viz_data[k][3])
            if(n > -1):
                sizes.append(s)
                num_of_packages.append(n)
                x_dim.append(k)
        plot_ip_to_package_and_size(viz_data, ip_src_dst, sizes, num_of_packages, q)

if __name__ == "__main__":
    main()
