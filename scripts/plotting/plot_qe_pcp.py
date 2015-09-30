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

    # inspiration from http://www.randalolson.com/2014/06/28/how-to-make-beautiful-data-visualizations-in-python-with-matplotlib/
    tableau20 =  [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),  
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),  
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),  
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),  
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]  

    for i in range(len(tableau20)):  
        r, g, b = tableau20[i]  
        tableau20[i] = (r / 255., g / 255., b / 255.)  


    marker = ['s', 'o', 'v', '^',  '>', '<', '8', 'H', 'p', '$\\bigoplus$', '*', 'd']

    idx = 0
    ps = []
    for q in qs:
        p, = ax1.plot(mea_time, q, 'b-', color=tableau20[idx], marker=marker[idx], label=labels[idx])
        ps.append(p)
        idx = idx + 1

    ax1.set_xlabel('time (minutes)')
    ax1.set_ylabel(y_label, color='b')

    plt.legend()
    plt.savefig(target_file)


def plot(data_file, fields, labels, plot_file_prefix, output_dir):

    qes = []
    
    for l in labels:
        q = {}
        for f in fields:
            q[f] = []
        q["label"] = l 
        qes.append(q)

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
        result_picture = "{0}/{1}_{2}.jpeg".format(output_dir, plot_file_prefix, f)
        result_picture = result_picture.replace(" ", "_")
        generate_graph(meas, mea_time, y_label, result_picture, labels)



def get_data_for(pcp_data_dir, output_dir, result_file_prefix,
                             instances_num, from_time, till_time,
                             experiment_date, val_template):

    result_file = "{0}/{1}_mem_load.txt".format(output_dir, result_file_prefix)

    os.system("rm -f {0}/{1}".format(output_dir, result_file))

    input_files = []
    val_declarations = []

    for inst_num in instances_num:
        v_d = val_template.format(inst_num)
        if inst_num == 8: #  NOTICE: HACK FOR LEADS-QE8
            v_d = v_d.replace("-", "")
        val_declarations.append(v_d)
        input_files.append("leads-qe{0}/20150916.0".format(inst_num))        

    cmd = """
    cd {0} ; pmdumptext  -t 30sec -i -l -S @'{2}' -T @'{3}' \
    {1} -a {4} > {5}
    """.format(pcp_data_dir, " ".join(val_declarations),  from_time, till_time,
        ",".join(input_files), result_file)
    os.system(cmd)
    return result_file


def get_data_for_mem_and_cpu(pcp_data_dir, output_dir, result_file_prefix,
                             instances_num, from_time, till_time,
                             experiment_date):
    tmpl = "'leads-qe{0}:kernel.all.load[1]' 'leads-qe{0}:mem.util.used'"
    return get_data_for(pcp_data_dir, output_dir, result_file_prefix,
                        instances_num, from_time, till_time,
                        experiment_date,
                        tmpl)


# 'leads-qe2:network.interface.in.bytes' 'leads-qe2:network.interface.out.bytes'\

def get_data_for_network_in_out_bytes(pcp_data_dir, output_dir, result_file_prefix,
                                      instances_num, from_time, till_time,
                                      experiment_date):
    tmpl = "'leads-qe{0}:network.interface.in.bytes' 'leads-qe{0}:network.interface.out.bytes'"
    return get_data_for(pcp_data_dir, output_dir, result_file_prefix,
                        instances_num, from_time, till_time,
                        experiment_date,
                        tmpl)

def get_data_for_disk_read_write_bytes(pcp_data_dir, output_dir, result_file_prefix,
                                      instances_num, from_time, till_time,
                                      experiment_date):
    tmpl = "'leads-qe{0}:disk.all.write_bytes' 'leads-qe{0}:disk.all.read_bytes'"
    return get_data_for(pcp_data_dir, output_dir, result_file_prefix,
                        instances_num, from_time, till_time,
                        experiment_date,
                        tmpl)


# https://redmine.cloudandheat.com/issues/4674
def plot_one_for_all_q(pcp_data_dir, output_dir, result_file_prefix,
            instances_num, labels, experiment_date):

    plot_query( 
        pcp_data_dir, output_dir, result_file_prefix,
        instances_num, labels, experiment_date,
        "2015-09-16 09:33",
        "2015-09-16 10:11")


# https://redmine.cloudandheat.com/issues/4674
def plot_q1(pcp_data_dir, output_dir, result_file_prefix,
            instances_num, labels, experiment_date):

    plot_query( 
        pcp_data_dir, output_dir, result_file_prefix,
        instances_num, labels, experiment_date,
        "2015-09-16 09:38",
        "2015-09-16 09:39")


# https://redmine.cloudandheat.com/issues/4674
def plot_q2(pcp_data_dir, output_dir, result_file_prefix,
            instances_num, labels, experiment_date):

    plot_query( 
        pcp_data_dir, output_dir, result_file_prefix,
        instances_num, labels, experiment_date,
        "2015-09-16 09:41",
        "2015-09-16 09:46")


# https://redmine.cloudandheat.com/issues/4674
def plot_q3(pcp_data_dir, output_dir, result_file_prefix,
            instances_num, labels, experiment_date):

    plot_query( 
        pcp_data_dir, output_dir, result_file_prefix,
        instances_num, labels, experiment_date,
        "2015-09-16 09:47",
        "2015-09-16 09:59")

# https://redmine.cloudandheat.com/issues/4674
def plot_q4(pcp_data_dir, output_dir, result_file_prefix,
            instances_num, labels, experiment_date):

    plot_query( 
        pcp_data_dir, output_dir, result_file_prefix,
        instances_num, labels, experiment_date,
        "2015-09-16 10:00",
        "2015-09-16 10:04")

# https://redmine.cloudandheat.com/issues/4674
def plot_q5(pcp_data_dir, output_dir, result_file_prefix,
            instances_num, labels, experiment_date):

    plot_query( 
        pcp_data_dir, output_dir, result_file_prefix,
        instances_num, labels, experiment_date,
        "2015-09-16 10:05:00",
        "2015-09-16 10:05:30")

# https://redmine.cloudandheat.com/issues/4674
def plot_q6(pcp_data_dir, output_dir, result_file_prefix,
            instances_num, labels, experiment_date):

    plot_query( 
        pcp_data_dir, output_dir, result_file_prefix,
        instances_num, labels, experiment_date,
        "2015-09-16 10:05:30",
        "2015-09-16 10:05:59")


def plot_query(pcp_data_dir, output_dir, result_file_prefix,
              instances_num, labels, experiment_date,
              from_time, till_time):
    result_file = get_data_for_mem_and_cpu(pcp_data_dir, 
                                           output_dir,
                                           result_file_prefix,
                                           instances_num,
                                           from_time,
                                           till_time, 
                                           experiment_date)
    plot(result_file, ["kernel load", "memory used"], labels, result_file_prefix, output_dir)

    chunks_num = arr_to_chunks(instances_num, 1)
    chunks_labels = arr_to_chunks(labels, 1)

    print chunks_num
    print len(chunks_num)
    for i in xrange(0, len(chunks_num)):
        inst_num = chunks_num[i]
        inst_labels = chunks_labels[i]

        result_file = get_data_for_network_in_out_bytes(pcp_data_dir, 
                                                        output_dir,
                                                        result_file_prefix,
                                                        inst_num,
                                                        from_time,
                                                        till_time, 
                                                        experiment_date)
        plot(result_file, ["network received bytes", "network sent bytes"], inst_labels, result_file_prefix + "_" + str(i) , output_dir)

        result_file = get_data_for_disk_read_write_bytes(pcp_data_dir, 
                                                         output_dir,
                                                         result_file_prefix,
                                                         inst_num,
                                                         from_time,
                                                         till_time, 
                                                         experiment_date)
        plot(result_file, ["write bytes to disk", "read bytes from disk"], inst_labels, result_file_prefix + "_" + str(i), output_dir)


def arr_to_chunks(lst,n):
    return [ lst[i::n] for i in xrange(n) ]

if __name__ == "__main__":

    pcp_data_dir = os.environ["LEADS_PCP_DATA_DIR"]
    output_dir = os.environ["LEADS_PCP_FIGURE_DIR"]

    dd1a_instances = [14, 15, 22] #  8
    dd2a_instances = [41, 42, 43, 47]
    dd2c_instances = [28, 29, 33, 37]
    instances_num = dd1a_instances + dd2a_instances + dd2c_instances
    labels = ["qe-{0}".format(n) for n in instances_num]

    experiment_date = "20150916"

    plot_one_for_all_q(pcp_data_dir, output_dir, "qe_all",
                       instances_num,
                       labels,
                       experiment_date)

    #plot_q1(pcp_data_dir, output_dir, "qe1",
    #        instances_num,
    #        labels,
    #        experiment_date)

    #plot_q2(pcp_data_dir, output_dir, "qe2",
    #        instances_num,
    #        labels,
    #        experiment_date)

    #plot_q3(pcp_data_dir, output_dir, "qe3",
    #        instances_num,
    #        labels,
    #        experiment_date)


    #plot_q4(pcp_data_dir, output_dir, "qe4",
    #        instances_num,
    #        labels,
    #        experiment_date)


    #plot_q5(pcp_data_dir, output_dir, "qe5",
    #        instances_num,
    #        labels,
    #        experiment_date)

    #plot_q6(pcp_data_dir, output_dir, "qe6",
    #        instances_num,
    #        labels,
    #        experiment_date)
