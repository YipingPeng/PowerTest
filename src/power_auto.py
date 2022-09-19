import shlex
import subprocess
import Monsoon.HVPM as HVPM
import Monsoon.sampleEngine as sampleEngine
from android_tools import AndroidTool
from ios_tools import IOSTool
from generate_report import write_xlsx
from appium_auto import AndroidAppium, IOSAppium
from test_analyze import *
from video_tool import Video
import yaml
import os
import shutil
import click

test_clips_path = os.path.join(os.path.abspath(".."), "Test_Clips")
json_location = os.getcwd()
with open(r'../config/test_case.yml', "r") as f:
    test_case_list = yaml.load(f, Loader=yaml.FullLoader)
f.close()
with open(r'../config/pq_list.yml', "r") as f:
    pq_list = yaml.load(f, Loader=yaml.FullLoader)
f.close()


def setup_monsoon():
    mon = HVPM.Monsoon()
    mon.setup_usb()
    mon.setVout(4.2)
    # enable the engine
    engine = sampleEngine.SampleEngine(mon)
    engine.ConsoleOutput(True)

    return engine


def android_set_up():
    AndroidTool.push_video(test_clips_path, "sdcard/Movies/")
    test_vector = AndroidTool.get_video_list_from_storage("sdcard/Movies/")
    AndroidTool.write_json(test_vector, "sdcard/Movies/", json_location)
    js = os.path.join(json_location, os.path.join(os.path.abspath(".."), "dolby.exolist.json"))
    pq = os.path.join(json_location, '../PQ_config/Redmi_Note_9_Pro/dolby_vision.cfg')
    AndroidTool.push_file(js, "sdcard/Movies/")
    AndroidTool.push_file(pq, "sdcard/Movies/")
    print("Done preparation")


def ios_set_up():
    # create a folder to access app internal folder
    player_folder_name = "ios-sample-player"
    try:
        os.mkdir(player_folder_name)
    except Exception:
        pass
    # mount the app
    IOSTool.mount_app("com.globallogic.dvdecoding", player_folder_name)
    if "video" not in os.listdir("ios-sample-player"):
        os.mkdir(os.path.join(os.path.abspath("ios-sample-player"), "video"))
    IOSTool.push_video(test_clips_path, "ios-sample-player/video")
    return player_folder_name


def ios_tear_down(folder_name):
    # unmount the app
    IOSTool.umount_app(folder_name)
    # delete the folder
    try:
        shutil.rmtree(folder_name)
    except:
        pass


def adrd():
    if not AndroidTool.is_phone_connected():
        print("Device not connected. System exits.")
        sys.exit(1)

    desired_cap = {
        'platformName': f'Android',
        'platformVersion': f'{AndroidTool.get_device_os_version()}',
        'udid': f'{AndroidTool.get_udid()}',
        'newCommandTimeout': 60000,
        'automationName': 'UiAutomator2',
        'autoGrantPermissions': True
    }

    android_set_up()

    # engine = setup_monsoon()
    auto = AndroidAppium(desired_cap)

    # normal test cases
    result_dic = {}
    for test_case in test_case_list.keys():
        result_dic[test_case] = {}
        if test_case == "low-power-mode-test":
            # low power mode test cases
            AndroidTool.change_mode(pq_file=pq_list[AndroidTool.get_udid()], low_power_mode=1)
        else:
            AndroidTool.change_mode(pq_file=pq_list[AndroidTool.get_udid()], low_power_mode=0)

        for tv_name in test_case_list[test_case]:
            for root, dirs, files, in os.walk('../Test_Clips'):
                for file in files:
                    if tv_name in file:
                        test_vector = Video(root, file)
                        video_length = test_vector.get_video_length()
            for result_type in result_dic.keys():
                if tv_name not in result_dic[result_type].keys():
                    result_dic[result_type][tv_name] = []

            for i in range(3):
                if test_case == "gallery-test":
                    auto.launch_gallery()
                    if auto.click_on("Storage") or auto.click_on("STORAGE"):
                        pass
                    else:
                        sys.exit(1)
                    # swipe to the top
                    while auto.swipe(0):
                        pass
                    # start searching for the element, if not found, keep swiping down until the end
                    while True:
                        if auto.click_on("Movies"):
                            break
                        else:
                            if auto.swipe(1):
                                pass
                            else:
                                print("Couldn't find the folder")
                                auto.exit_gallery()
                                # os.system("adb wait-for-device shell am force-stop com.android.fileexplorer")
                                sys.exit(1)
                    # swpie to the top
                    while auto.swipe(0):
                        pass
                    # start searching for the element, if not found, keep swiping down until the end
                    while True:
                        if auto.click_on(tv_name):
                            # start measuring and write output csv file
                            # flname = "Android_"test_case + "_" + tv_name + "_" + str(i + 1) + ".csv"
                            # engine.enableCSVOutput(flname)
                            # engine.startSampling(5000 * (int(video_length) + 3))
                            # result_dic[test_case][tv_name].append(analyze_data_filter(flname))
                            auto.exit_gallery()
                            # os.system("adb wait-for-device shell am force-stop com.android.fileexplorer")
                            break
                        else:
                            if auto.swipe(1):
                                pass
                            else:
                                print("Couldn't find the content")
                                auto.exit_gallery()
                                # os.system("adb wait-for-device shell am force-stop com.android.fileexplorer")
                                break
                else:
                    resample = 1
                    while resample:
                        auto.launch_exoplayer()
                        auto.set_landscape()
                        if test_case == "dolby-vision-disabled-test":
                            auto.disable_dv()
                        else:
                            auto.enable_dv()
                        while auto.swipe(0):
                            pass
                        while True:
                            if auto.click_on("power test"):
                                break
                            else:
                                if auto.swipe(1):
                                    pass
                                else:
                                    print("Couldn't find the test list")
                                    auto.exit_exoplayer()
                                    # os.system("adb wait-for-device shell am force-stop "
                                    #           "com.google.android.exoplayer2.demo")
                                    sys.exit(1)
                        while auto.swipe(0):
                            pass
                        while True:
                            if auto.click_on(tv_name):
                                # pause the video
                                AndroidTool.pause_resume_video()
                                # drag the seekbar to see if the exoplayer crashes
                                if auto.drag_seekbar(50) and auto.drag_seekbar(0):
                                    AndroidTool.pause_resume_video()
                                    # write output csv file
                                    # flname = "Android_"+test_case + "_" + tv_name + "_" + str(i + 1) + ".csv"
                                    # engine.enableCSVOutput(flname)
                                    # engine.startSampling(5000 * video_length)
                                    # result_dic[test_case][tv_name].append(analyze_data_filter(flname))
                                    # os.system("adb wait-for-device shell am force-stop "
                                    #           "com.google.android.exoplayer2.demo")
                                    auto.exit_exoplayer()
                                    resample = 0
                                    break
                                else:
                                    print("Playback failed")
                                    # os.system(
                                    #     "adb wait-for-device shell am force-stop com.google.android.exoplayer2.demo")
                                    auto.exit_exoplayer()
                                    break
                            else:
                                if auto.swipe(1):
                                    pass
                                else:
                                    print("Couldn't find the content")
                                    # os.system("adb wait-for-device shell am force-stop "
                                    #           "com.google.android.exoplayer2.demo")
                                    auto.exit_exoplayer()
                                    break

    # write_xlsx('test.xlsx',result_dic["std"], result_dic["disable dv"], result_dic["low power"], result_dic[
    # "gallery"])
    # when all test cases were covered, change the pq config file back to normal mode
    AndroidTool.change_mode(pq_file=pq_list[AndroidTool.get_udid()], low_power_mode=0)


def ios():
    # device_name, udid, device_os_version
    if not IOSTool.is_phone_connected():
        print("Device not connected. System exits.")
        sys.exit(1)

    mount_folder = ios_set_up()
    # engine = setup_monsoon()

    # normal test cases
    result_dic = {}
    for test_case in test_case_list.keys():
        result_dic[test_case] = {}
        if test_case == "low-power-mode-test":
            # low power mode test cases
            IOSTool.change_mode(pq_file=pq_list[IOSTool.get_udid()], o_path=mount_folder, low_power_mode=1)
        else:
            IOSTool.change_mode(pq_file=pq_list[IOSTool.get_udid()], o_path=mount_folder, low_power_mode=0)

        for tv_name in test_case_list[test_case]:
            for root, dirs, files, in os.walk('../Test_Clips'):
                for file in files:
                    if tv_name in file:
                        test_vector = Video(os.path.join(root,file))
                        video_length = test_vector.get_video_length()
            for result_type in result_dic.keys():
                if tv_name not in result_dic[result_type].keys():
                    result_dic[result_type][tv_name] = []

            for i in range(3):
                if test_case == "gallery-test":
                    auto = IOSAppium(IOSTool.get_device_name(), IOSTool.get_udid(), IOSTool.get_device_os_version())
                    auto.exit_files_app()
                    auto.launch_files_app()
                    auto.set_landscape()
                    if auto.click_on("Browse"):
                        pass
                    else:
                        sys.exit(1)

                    if auto.click_on("On My iPhone"):
                        pass
                    else:
                        sys.exit(1)
                    # start searching for the element, if not found, keep swiping down until the end
                    while True:
                        if auto.click_on("power test"):
                            break
                        else:
                            if auto.swipe(1):
                                pass
                            else:
                                print("Couldn't find the folder")
                                sys.exit(1)
                    while True:
                        if auto.click_on(tv_name):
                            auto.click_on("Play")
                            # # write output csv file
                            # flname = "../test_results/iOS_" + test_case + "_" + tv_name + "_" + str(i + 1) + ".csv"
                            # engine.enableCSVOutput(flname)
                            # engine.startSampling(5000 * video_length)
                            # cmd = f"python3 test_analyze.py --file {flname}"
                            # subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            # result_dic[test_case][tv_name].append(analyze_data_filter(flname))
                            time.sleep(5)
                            break
                        else:
                            if auto.swipe(1):
                                pass
                            else:
                                print("Couldn't find the content")
                                auto.exit_files_app()
                                break
                    auto.driver.quit()
                else:
                    continue
                    resample = 1
                    while resample:
                        auto = IOSAppium(IOSTool.get_device_name(), IOSTool.get_udid(), IOSTool.get_device_os_version())
                        auto.exit_ios_sample_player()
                        auto.launch_ios_sample_player()
                        # auto.set_landscape()
                        if test_case == "dolby-vision-disabled-test":
                            auto.disable_dv()
                            auto.exit_ios_sample_player()
                            auto.launch_ios_sample_player()
                        else:
                            auto.enable_dv()
                            auto.exit_ios_sample_player()
                            auto.launch_ios_sample_player()
                        while True:
                            if auto.click_on(tv_name):
                                # pause the video
                                auto.set_landscape()
                                auto.play_back()
                                # write output csv file
                                flname = "../test_results/iOS_" + test_case + "_" + tv_name + "_" + str(i + 1) + ".csv"
                                engine.enableCSVOutput(flname)
                                engine.startSampling(5000 * video_length)
                                cmd = f"python3 test_analyze.py --file {flname}"
                                subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                result_dic[test_case][tv_name].append(analyze_data_filter(flname))
                                time.sleep(5)
                                resample = 0
                                break
                            else:
                                if auto.swipe(1):
                                    pass
                                else:
                                    print("Couldn't find the content")
                                    break
                        auto.driver.quit()

    IOSTool.change_mode(pq_file=pq_list[IOSTool.get_udid()], o_path=mount_folder, low_power_mode=0)
    ios_tear_down(mount_folder)


if __name__ == '__main__':
    # analyze_data("std_PWT-avc_sdr_8b-720P-MP4-23_976_1.csv")
    # adrd()
    ios()
