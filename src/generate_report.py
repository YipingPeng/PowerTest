import os
import sys
import xlsxwriter
from test_analyze import analyze_data_filter
from android_tools import *
from openpyxl import Workbook, load_workbook


def write_xlsx(*args):
    pass


def write_xlsx(filename, std_dic, disabled_dic, low_dic, gallery_dic):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    sdr_title = ['SDR Content Format', 'Player & Configuration', 'Test Case', 'Run 1(mW)', 'Run 2(mW)', 'Run 3(mW)',
                 'Average (mW)', 'Comment']
    dv_title = ['DV Content Format', 'Player & Configuration', 'Test Case', 'Run 1(mW)', 'Run 2(mW)', 'Run 3(mW)',
                'Average (mW)', 'Comment', 'DV vs. SDR (Exo with Extension)', 'DV vs. SDR (Gallery)']

    # set width of the column
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 24)
    worksheet.set_column('C:C', 36)
    worksheet.set_column('D:D', 10)
    worksheet.set_column('E:E', 10)
    worksheet.set_column('F:F', 10)
    worksheet.set_column('G:G', 13)
    worksheet.set_column('H:H', 36)
    worksheet.set_column('I:I', 12)

    device_info = workbook.add_format({'bold': True,
                                       'border': 1,
                                       'fg_color': '#d9e1f2'})
    bold = workbook.add_format({'bold': True,
                                'border': 1,
                                'align': 'center',
                                'valign': 'vcenter',
                                'text_wrap': 1})
    title = workbook.add_format({'fg_color': 'yellow',
                                 'bold': 1,
                                 'align': 'center',
                                 'valign': 'vcenter',
                                 'border': 1,
                                 'text_wrap': 1})
    border = workbook.add_format({'border': 1})
    compare = workbook.add_format({'border': 1,
                                   'num_format': '0.00%',
                                   'align': 'center',
                                   'valign': 'vcenter'})
    data = workbook.add_format({'border': 1,
                                'align': 'center',
                                'valign': 'vcenter'})
    split_grey = workbook.add_format({'fg_color': '#d9d9d9', 'border': 1})
    avg_green = workbook.add_format({'fg_color': '#e2efda',
                                     'border': 1,
                                     'align': 'center',
                                     'valign': 'vcenter',
                                     'num_format': "0.00"})
    # Average formula
    formula_avg = r'=AVERAGE(D_tmp,E_tmp,F_tmp)'
    # dv_sdr comparison formula
    formula_compare = r'=(Gtmp-GTmp)/GTmp'

    worksheet.write(0, 0, 'SoC', device_info)
    worksheet.write(1, 0, 'Android OS version:', device_info)
    worksheet.write(2, 0, 'Panel brightness:', device_info)
    worksheet.write(0, 1, '', device_info)
    worksheet.write(1, 1, '', device_info)
    worksheet.write(2, 1, '', device_info)

    for i in range(len(sdr_title)):
        for j in range(4, 46):
            worksheet.write(j, i, '', border)
    for i in range(len(dv_title)):
        for j in range(49, 90):
            worksheet.write(j, i, '', border)
    for i in range(len(sdr_title)):
        worksheet.write(25, i, '', split_grey)
    for i in range(len(dv_title)):
        worksheet.write(62, i, '', split_grey)
        worksheet.write(76, i, '', split_grey)
    for j in range(5, 11):
        for k in range(6):
            worksheet.write_formula(j + 7 * k, 6,
                                    formula_avg.replace('D_tmp', 'D' + str(j + 7 * k + 1)).replace('E_tmp', 'E' + str(
                                        j + 7 * k + 1)).replace('F_tmp', 'F' + str(j + 7 * k + 1)), avg_green)
    for k in range(3):
        worksheet.write(5 + k * 7, 2, 'PWT-avc_sdr_8b-720P-MP4-23_976', border)
        worksheet.write(6 + k * 7, 2, 'PWT-avc_sdr_8b-720P-MP4-29_97', border)
        worksheet.write(7 + k * 7, 2, 'PWT-avc_sdr_8b-720P-MP4-59_94', border)
        worksheet.write(8 + k * 7, 2, 'PWT-avc_sdr_8b-FHD-MP4-23_976', border)
        worksheet.write(9 + k * 7, 2, 'PWT-avc_sdr_8b-FHD-MP4-29_97', border)
        worksheet.write(10 + k * 7, 2, 'PWT-avc_sdr_8b-FHD-MP4-59_94', border)

        worksheet.write(26 + k * 7, 2, 'PWT-hevc_sdr_10b-FHD-MP4-23_976', border)
        worksheet.write(27 + k * 7, 2, 'PWT-hevc_sdr_10b-FHD-MP4-29_97', border)
        worksheet.write(28 + k * 7, 2, 'PWT-hevc_sdr_10b-FHD-MP4-59_94', border)
        worksheet.write(29 + k * 7, 2, 'PWT-hevc_sdr_10b-UHD-MP4-23_976', border)
        worksheet.write(30 + k * 7, 2, 'PWT-hevc_sdr_10b-UHD-MP4-29_97', border)
        worksheet.write(31 + k * 7, 2, 'PWT-hevc_sdr_10b-UHD-MP4-59_94', border)
    for k in range(2):
        worksheet.write(49 + k * 7, 2, 'PWT-dvhe.05_00-FHD-MP4-23_976', border)
        worksheet.write(50 + k * 7, 2, 'PWT-dvhe.05_00-FHD-MP4-29_97', border)
        worksheet.write(51 + k * 7, 2, 'PWT-dvhe.05_00-FHD-MP4-59_94', border)
        worksheet.write(52 + k * 7, 2, 'PWT-dvhe.05_00-UHD-MP4-23_976', border)
        worksheet.write(53 + k * 7, 2, 'PWT-dvhe.05_00-UHD-MP4-29_97', border)
        worksheet.write(54 + k * 7, 2, 'PWT-dvhe.05_00-UHD-MP4-59_94', border)

        worksheet.write(63 + k * 7, 2, 'PWT-dvhe.08_04-FHD-MP4-23_976', border)
        worksheet.write(64 + k * 7, 2, 'PWT-dvhe.08_04-FHD-MP4-29_97', border)
        worksheet.write(65 + k * 7, 2, 'PWT-dvhe.08_04-FHD-MP4-59_94', border)
        worksheet.write(66 + k * 7, 2, 'PWT-dvhe.08_04-UHD-MP4-23_976', border)
        worksheet.write(67 + k * 7, 2, 'PWT-dvhe.08_04-UHD-MP4-29_97', border)
        worksheet.write(68 + k * 7, 2, 'PWT-dvhe.08_04-UHD-MP4-59_94', border)

        worksheet.write(77 + k * 7, 2, 'PWT-davc.32_03-CR-720p-MP4-23_976', border)
        worksheet.write(78 + k * 7, 2, 'PWT-davc.32_03-CR-720p-MP4-29_97', border)
        worksheet.write(79 + k * 7, 2, 'PWT-davc.32_03-CR-720p-MP4-59_94', border)
        worksheet.write(80 + k * 7, 2, 'PWT-davc.32_03-CR-FHD-MP4-23_976', border)
        worksheet.write(81 + k * 7, 2, 'PWT-davc.32_03-CR-FHD-MP4-29_97', border)
        worksheet.write(82 + k * 7, 2, 'PWT-davc.32_03-CR-FHD-MP4-59_94', border)
    for j in range(49, 55):
        for k in range(6):
            worksheet.write_formula(j + 7 * k, 6,
                                    formula_avg.replace('D_tmp', 'D' + str(j + 7 * k + 1)).replace('E_tmp', 'E' + str(
                                        j + 7 * k + 1)).replace('F_tmp', 'F' + str(j + 7 * k + 1)), avg_green)
            if k < 4:
                worksheet.write_formula(j + 7 * k, 8,
                                        formula_compare.replace('Gtmp', 'G' + str(j + 7 * k + 1)).replace('GTmp',
                                                                                                          'G' + str(
                                                                                                              27 + j - 49)),
                                        compare)
                worksheet.write_formula(j + 7 * k, 9,
                                        formula_compare.replace('Gtmp', 'G' + str(j + 7 * k + 1)).replace('GTmp',
                                                                                                          'G' + str(
                                                                                                              41 + j - 49)),
                                        compare)

            else:
                worksheet.write_formula(j + 7 * k, 8,
                                        formula_compare.replace('Gtmp', 'G' + str(j + 7 * k + 1)).replace('GTmp',
                                                                                                          'G' + str(
                                                                                                              6 + j - 49)),
                                        compare)
                worksheet.write_formula(j + 7 * k, 9,
                                        formula_compare.replace('Gtmp', 'G' + str(j + 7 * k + 1)).replace('GTmp',
                                                                                                          'G' + str(
                                                                                                              20 + j - 49)),
                                        compare)

    for i in range(len(sdr_title)):
        worksheet.write(4, i, sdr_title[i], title)
    for j in range(len(dv_title)):
        worksheet.write(48, j, dv_title[j], title)

    worksheet.merge_range('A6:A25', 'AVC 8-bit SDR', bold)
    worksheet.merge_range('A27:A46', 'HEVC 10-bit SDR', bold)
    worksheet.merge_range('A50:A62', 'Profile 5', bold)
    worksheet.merge_range('A64:A76', 'Profile 8.4', bold)
    worksheet.merge_range('A78:A90', 'Profile 32.3', bold)

    worksheet.merge_range('B6:B11', 'Exoplayer with extension decoder', bold)
    worksheet.merge_range('B13:B18', 'Exoplayer without extension decoder', bold)
    worksheet.merge_range('B20:B25', 'Gallery', bold)
    worksheet.merge_range('B27:B32', 'Exoplayer with extension decoder', bold)
    worksheet.merge_range('B34:B39', 'Exoplayer without extension decoder', bold)
    worksheet.merge_range('B41:B46', 'Gallery', bold)
    worksheet.merge_range('B50:B55', 'Standard mode', bold)
    worksheet.merge_range('B57:B62', 'low power mode', bold)
    worksheet.merge_range('B64:B69', 'Standard mode', bold)
    worksheet.merge_range('B71:B76', 'low power mode', bold)
    worksheet.merge_range('B78:B83', 'Standard mode', bold)
    worksheet.merge_range('B85:B90', 'low power mode', bold)

    # record data of std_list, low_list, disabled_list, gallery_list

    for i in range(int(len(std_dic) / 5)):
        idx = list(std_dic.keys())[i]
        worksheet.write(5 + i, 3, std_dic[idx][0], data)
        worksheet.write(5 + i, 4, std_dic[idx][1], data)
        worksheet.write(5 + i, 5, std_dic[idx][2], data)
    for i in range(int(len(std_dic) / 5), int(len(std_dic) / 5) * 2):
        idx = list(std_dic.keys())[i]
        worksheet.write(77 + i - int(len(std_dic) / 5), 3, std_dic[idx][0], data)
        worksheet.write(77 + i - int(len(std_dic) / 5), 4, std_dic[idx][1], data)
        worksheet.write(77 + i - int(len(std_dic) / 5), 5, std_dic[idx][2], data)
    for i in range(int(len(std_dic) / 5) * 2, int(len(std_dic) / 5) * 3):
        idx = list(std_dic.keys())[i]
        worksheet.write(49 + i - int(len(std_dic) / 5 * 2), 3, std_dic[idx][0], data)
        worksheet.write(49 + i - int(len(std_dic) / 5 * 2), 4, std_dic[idx][1], data)
        worksheet.write(49 + i - int(len(std_dic) / 5 * 2), 5, std_dic[idx][2], data)
    for i in range(int(len(std_dic) / 5) * 3, int(len(std_dic) / 5) * 4):
        idx = list(std_dic.keys())[i]
        worksheet.write(63 + i - int(len(std_dic) / 5 * 3), 3, std_dic[idx][0], data)
        worksheet.write(63 + i - int(len(std_dic) / 5 * 3), 4, std_dic[idx][1], data)
        worksheet.write(63 + i - int(len(std_dic) / 5 * 3), 5, std_dic[idx][2], data)
    for i in range(int(len(std_dic) / 5) * 4, int(len(std_dic) / 5) * 5):
        idx = list(std_dic.keys())[i]
        worksheet.write(26 + i - int(len(std_dic) / 5 * 4), 3, std_dic[idx][0], data)
        worksheet.write(26 + i - int(len(std_dic) / 5 * 4), 4, std_dic[idx][1], data)
        worksheet.write(26 + i - int(len(std_dic) / 5 * 4), 5, std_dic[idx][2], data)

    # disable extension decoder feature
    for i in range(int(len(disabled_dic) / 2)):
        idx = list(disabled_dic.keys())[i]
        worksheet.write(12 + i, 3, disabled_dic[idx][0], data)
        worksheet.write(12 + i, 4, disabled_dic[idx][1], data)
        worksheet.write(12 + i, 5, disabled_dic[idx][2], data)
    for i in range(int(len(disabled_dic) / 2), len(disabled_dic)):
        idx = list(disabled_dic.keys())[i]
        worksheet.write(33 + i - int(len(disabled_dic) / 2), 3, disabled_dic[idx][0], data)
        worksheet.write(33 + i - int(len(disabled_dic) / 2), 4, disabled_dic[idx][1], data)
        worksheet.write(33 + i - int(len(disabled_dic) / 2), 5, disabled_dic[idx][2], data)

    # gallery feature
    for i in range(int(len(gallery_dic) / 2)):
        idx = list(gallery_dic.keys())[i]
        worksheet.write(19 + i, 3, gallery_dic[idx][0], data)
        worksheet.write(19 + i, 4, gallery_dic[idx][1], data)
        worksheet.write(19 + i, 5, gallery_dic[idx][2], data)
    for i in range(int(len(gallery_dic) / 2), len(gallery_dic)):
        idx = list(gallery_dic.keys())[i]
        worksheet.write(40 + i - int(len(gallery_dic) / 2), 3, gallery_dic[idx][0], data)
        worksheet.write(40 + i - int(len(gallery_dic) / 2), 4, gallery_dic[idx][1], data)
        worksheet.write(40 + i - int(len(gallery_dic) / 2), 5, gallery_dic[idx][2], data)

    # low power feature
    for i in range(int(len(low_dic) / 3)):
        idx = list(low_dic.keys())[i]
        worksheet.write(56 + i, 3, low_dic[idx][0], data)
        worksheet.write(56 + i, 4, low_dic[idx][1], data)
        worksheet.write(56 + i, 5, low_dic[idx][2], data)
    for i in range(int(len(low_dic) / 3), int(len(low_dic) / 3) * 2):
        idx = list(low_dic.keys())[i]
        worksheet.write(70 + i - int(len(low_dic) / 3), 3, low_dic[idx][0], data)
        worksheet.write(70 + i - int(len(low_dic) / 3), 4, low_dic[idx][1], data)
        worksheet.write(70 + i - int(len(low_dic) / 3), 5, low_dic[idx][2], data)
    for i in range(int(len(low_dic) / 3) * 2, int(len(low_dic))):
        idx = list(low_dic.keys())[i]
        worksheet.write(84 + i - int(len(low_dic) / 3) * 2, 3, low_dic[idx][0], data)
        worksheet.write(84 + i - int(len(low_dic) / 3) * 2, 4, low_dic[idx][1], data)
        worksheet.write(84 + i - int(len(low_dic) / 3) * 2, 5, low_dic[idx][2], data)

    workbook.close()


def main():
    all_test_vector = get_mp4("sdcard/Movies/")
    sdr = ["PWT-avc_sdr_8b-720P-MP4-23_976", "PWT-avc_sdr_8b-720P-MP4-29_97", "PWT-avc_sdr_8b-720P-MP4-59_94",
           "PWT-avc_sdr_8b-FHD-MP4-23_976", "PWT-avc_sdr_8b-FHD-MP4-29_97", "PWT-avc_sdr_8b-FHD-MP4-59_94",
           "PWT-hevc_sdr_10b-FHD-MP4-23_976", "PWT-hevc_sdr_10b-FHD-MP4-29_97", "PWT-hevc_sdr_10b-FHD-MP4-59_94",
           "PWT-hevc_sdr_10b-UHD-MP4-23_976", "PWT-hevc_sdr_10b-UHD-MP4-29_97", "PWT-hevc_sdr_10b-UHD-MP4-59_94"]
    dv = ["PWT-dvhe.05_00-FHD-MP4-23_976", "PWT-dvhe.05_00-FHD-MP4-29_97", "PWT-dvhe.05_00-FHD-MP4-59_94",
          "PWT-dvhe.05_00-UHD-MP4-23_976", "PWT-dvhe.05_00-UHD-MP4-29_97", "PWT-dvhe.05_00-UHD-MP4-59_94",
          "PWT-dvhe.08_04-FHD-MP4-23_976", "PWT-dvhe.08_04-FHD-MP4-29_97", "PWT-dvhe.08_04-FHD-MP4-59_94",
          "PWT-dvhe.08_04-UHD-MP4-23_976", "PWT-dvhe.08_04-UHD-MP4-29_97", "PWT-dvhe.08_04-UHD-MP4-59_94",
          "PWT-davc.32_03-CR-720p-MP4-23_976", "PWT-davc.32_03-CR-720p-MP4-29_97", "PWT-davc.32_03-CR-720p-MP4-59_94",
          "PWT-davc.32_03-CR-FHD-MP4-23_976", "PWT-davc.32_03-CR-FHD-MP4-29_97", "PWT-davc.32_03-CR-FHD-MP4-59_94"]
    test_case_dic = {"std": all_test_vector.keys(), "low power": dv, "disable dv": sdr, "gallery": sdr}
    # for item in os.listdir(r".\0brightness_dark"):
    #     if item.endswith(".csv"):
    #         analyze_data_filter(os.path.join(os.getcwd()+r'\0brightness_dark', item))
    result_dic = {"std": {}, "disable dv": {}, "low power": {}, "gallery": {}}
    for feature in test_case_dic.keys():
        for test_case in test_case_dic[feature]:
            for item in os.listdir(r".\Mi10_50brightness_bright"):
                if item.endswith(".txt"):
                    if feature in item and test_case in item:
                        if test_case not in result_dic[feature].keys():
                            result_dic[feature][test_case] = []
                        with open(os.path.join(os.getcwd() + r'\Mi10_50brightness_bright', item), "r") as file:
                            try:
                                result_dic[feature][test_case].append(float(file.read()))
                            except:
                                print(feature)
                                print(test_case)
                                print(file.read())
                                sys.exit()
                        file.close()
    write_xlsx("Mi10_50brightness_bright.xlsx", result_dic["std"], result_dic["disable dv"], result_dic["low power"],
               result_dic["gallery"])


if __name__ == '__main__':
    main()
