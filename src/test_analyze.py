import time
import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
import logging
import click


def analyze_data_filter(filename):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    logging.info("Starts parsing.")
    t1 = time.time()    # Start time
    f = open(filename, 'r')
    reader = csv.reader(f)
    power_dic = {}
    for row in reader:
        try:
            # p = M*V
            pwr = float(row[1]) * float(row[2])
            power_dic.setdefault(round(float(row[0]),2), [])
            power_dic[round(float(row[0]),2)].append(pwr)
        except ValueError:
            pass

    for key in power_dic.keys():
        power_dic[key] = np.mean(power_dic[key])

    plt.figure()
    plt.xlabel("time(s)")
    plt.ylabel("power(mW)")
    # plot the raw data
    plt.plot(power_dic.keys(), power_dic.values())

    # class interval
    distance = 25
    # Group of Number
    GON = int((max(power_dic.values()) - min(power_dic.values())) / distance)
    # get the histogram of the raw data
    y, x = np.histogram(list(power_dic.values()), bins=GON)  # y is the frequency, x is bin
    # plt.hist(list(power_dic.values()), bins=GON)

    # create a dictionary to sort the histogram
    hist_dic = {}
    for i in range(len(y)):
        hist_dic[tuple([x[i], x[i + 1]])] = y[i]  # key: frequency, value: interval
    # sort the histogram with descent order, starts with the highest frequency
    new_hist_dic = sorted(hist_dic.items(), key=lambda item: item[1], reverse=True)

    remove_list = list()
    total_ = sum([i[1] for i in new_hist_dic])
    sumup = 0
    for item in new_hist_dic:
        if sumup > total_ * 0.95:
            remove_list.append(item[0])
        sumup += item[1]

    for j in range(len(remove_list)):
        for k in list(power_dic.keys()):
            if remove_list[j][0] <= power_dic[k] <= remove_list[j][1]:
                power_dic.pop(k)
    plt.plot(power_dic.keys(), power_dic.values())

    # otsu's method
    total_length = len(power_dic)
    threshold = 0
    tmp = sys.maxsize

    tmp_x = list(power_dic.keys())
    tmp_y = list(power_dic.values())
    for i in range(int(total_length*4/5), total_length):
        if i == 0 or i == total_length:
            continue
        sigma = (i / total_length) * np.var(tmp_y[0:i]) + (
                    (total_length - i) / total_length) * np.var(tmp_y[i:])
        if sigma < tmp:
            threshold = i
            tmp = sigma

    final_x = tmp_x[0:threshold]
    final_y = tmp_y[0:threshold]
    best = round(np.mean(final_y), 2)
    logging.info("Average Power Usage: " + str(best) + " mW")
    t2 = time.time()
    time_taken = t2 - t1
    logging.info("Calculation takes " + str(time_taken) + "s long.")
    plt.plot(final_x, final_y)
    plt.savefig(filename[:-4] + r".jpg")
    plt.close()
    with open(filename[:-4] + r".txt", "w") as file:
        file.write(str(best))
    file.close()

    return best


def analyze_data_nofilter(filename):
    # parse the results
    print("Starts parsing")
    t1 = time.time()
    f = open(filename, 'r')
    reader = csv.reader(f)
    # tmp_dic[sec] = row of the sec
    tmp_dic = {}
    power_dic = {}

    for row in reader:
        try:
            # p = M*V
            if float(row[0]) > 83:
                break
            pwr = float(row[1]) * float(row[2])
            if round(float(row[0]), 2) not in power_dic.keys():
                power_dic[round(float(row[0]), 2)] = []
            power_dic[round(float(row[0]), 2)].append(pwr)

        except ValueError:
            pass
    # j = second
    j = 0
    for key in power_dic.keys():
        if len(tmp_dic) == int(key):
            tmp_dic[int(key)] = j
        power_dic[key] = np.mean(power_dic[key])
        j += 1

    pre = 0
    new_dic = {}
    for t in range(1, len(tmp_dic)):
        new_dic[t] = np.mean(list(power_dic.values())[pre:tmp_dic[t]])
        pre = tmp_dic[t]

    f.close()
    # plot the data
    plt.figure()
    plt.xlabel("Time(s)")
    plt.ylabel("Power(mW)")
    plt.plot(power_dic.keys(), power_dic.values())

    min_var = sys.maxsize
    best = 10000
    best_second = 0
    best_period = list(power_dic.keys())[0:0]

    best_sp = 25
    for second in range(len(new_dic) - best_sp):
        # variance the best_sp seconds data
        var_ = np.var(list(new_dic.values())[second:second + best_sp])
        # find the most stable one
        if var_ <= min_var:
            min_var = var_
            best_second = second
    best_period = list(power_dic.keys())[tmp_dic[best_second]:tmp_dic[best_second + best_sp]]
    best = np.mean(list(new_dic.values())[best_second:best_second + best_sp])
    print("Most Stable Average Power Usage: " + str(best) + " mW")
    print("It starts at " + str(list(power_dic.keys())[tmp_dic[best_second]]) + " s")

    t2 = time.time()
    time_taken = t2 - t1
    print("Calculation takes " + str(time_taken) + "s long.")
    # plot the best datas
    plt.plot(best_period, list(power_dic.values())[tmp_dic[best_second]:tmp_dic[best_second + best_sp]])
    plt.savefig(filename[:-4] + r".jpg")
    plt.close()

    return best


@click.command()
@click.option("--file", prompt="Please input your result file location",
              help="Specify the results folder path.")
def main(file):
    analyze_data_filter('../test_results/iOS_low-power-mode-test_PWT-dvhe.05_00-FHD-MP4-23_976_1.csv')


if __name__ == "__main__":
    main()
