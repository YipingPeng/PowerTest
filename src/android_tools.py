import json
import os
import time
import click
import re
import subprocess
import shlex
import logging
import shutil
from video_tool import Video


class AndroidTool:
    adb_path = shutil.which("adb") + " "
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    @staticmethod
    def is_phone_connected():
        cmd = AndroidTool.adb_path + f"devices"
        ret_out = subprocess.check_output(shlex.split(cmd), shell=False, ).decode().strip().splitlines()
        ret_out.pop(0)
        if ret_out:
            return True
        else:
            return False

    @staticmethod
    def push_file(i_path, o_path):
        cmd = AndroidTool.adb_path + f"wait-for-device push {i_path} {o_path}"
        logging.info("Executing: " + cmd)
        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

    @staticmethod
    def push_video(i_path, o_path):
        for root, dirs, files, in os.walk(i_path):
            for file in files:
                if Video.is_file_video(file):
                    cmd = AndroidTool.adb_path + f"wait-for-device push {os.path.join(root, file)} {o_path}"
                    logging.info("Executing: " + cmd)
                    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    p.wait()

    @staticmethod
    def get_video_list_from_storage(file_path):
        test_vectors = {}
        if os.path.exists(os.path.join(os.getcwd(), "../file_list.txt")):
            os.remove(os.path.join(os.getcwd(), "../file_list.txt"))
        os.system(AndroidTool.adb_path + " wait-for-device shell ls %s >> ../file_list.txt" % file_path)
        logging.debug(AndroidTool.adb_path + "wait-for-device shell ls %s >> ../file_list.txt" % file_path)
        while not os.path.exists(os.path.join(os.getcwd(), "../file_list.txt")):
            logging.debug("Waiting for file_list.txt to be generated.")
            time.sleep(2)
        with open("../file_list.txt", "r", encoding='utf8') as flist:
            for line in flist:
                if Video.is_file_video(line.strip()):
                    test_vectors[('.').join(line.strip().split('.')[:-1])] = line.strip()
        logging.info(f"Fetched test vectors:\n{test_vectors}")

        return test_vectors

    @staticmethod
    def write_json(test_vectors, file_path, json_location, json_folder="power test"):
        # test vectors name,
        video = list()
        for vector in test_vectors:
            tmp_dic = {
                "name": vector,
                "uri": "file:///" + file_path + test_vectors[vector]
            }
            video.append(tmp_dic)
        final_json = [{
            "name": json_folder,
            "samples": video
        }]

        json_str = json.dumps(final_json, ensure_ascii=False, indent=2)
        with open(os.path.join(json_location, '../dolby.exolist.json'), 'w', encoding='utf8') as json_file:
            json_file.write(json_str)
        logging.info(f"Created Json file:\n{final_json}")

        return json_file

    @staticmethod
    def get_case_name_from_json(json_list):
        try:
            file = open(json_list, "r")
            file_read = file.read()
            file_read = re.sub("\n", " ", file_read)
            # find "name": "" matching format
            case_list = re.findall(r'"name":\s"\b[^"]+\b"', file_read)
            # pop out the first one, because it's the menu name
            menu_name = case_list.pop(0).split(":")[1].replace('"', '').replace(" ", "")
            # rename the case name
            for i in range(len(case_list)):
                case_list[i] = menu_name + "+" + case_list[i].split(":")[1].replace('"', '').replace(" ", "")
            return case_list
        except:
            logging.error("File not exist")
            return None

    @staticmethod
    def get_device_os_version():
        device_version = None
        cmd = AndroidTool.adb_path + "shell getprop ro.build.version.release"
        ret_out = subprocess.check_output(shlex.split(cmd), shell=False,)
        if ret_out:
            device_version = int(str(ret_out, encoding="utf-8").replace("\n", ""))

        return device_version

    @staticmethod
    def get_udid():
        udid = None
        cmd = AndroidTool.adb_path + "wait-for-device devices"

        ret_out = subprocess.check_output(shlex.split(cmd), shell=False, ).decode()
        if ret_out.splitlines()[-2].split()[1] == "device":
            udid = ret_out.splitlines()[-2].split()[0]

        return udid

    @staticmethod
    def change_mode(pq_file, low_power_mode=1):
        if low_power_mode:
            mode = "low power mode"
        else:
            mode = "standard mode"
        logging.info(f"Changing to {mode}")

        with open(pq_file, "r+") as file:
            f = file.read()
            if f.find(f"LowPowerMode = ") != -1:
                file.seek(f.find(f"LowPowerMode = ") + 15)
                file.truncate()
                file.write(f"{low_power_mode}")
                file.write(f[f.find("LowPowerMode = ") + 16:])
            else:
                pos = min([f.find("[PictureMode = 0]"), f.find("[PictureMode = 1]"), f.find("[PictureMode = 2]")])
                file.seek(pos - 2)
                file.truncate()
                file.write(f"\nLowPowerMode = {low_power_mode}\n\n")
                file.write(f[pos:])
        file.close()

        logging.info("Executing: " + AndroidTool.adb_path + f"wait-for-device push {pq_file} sdcard/Movies/")
        p = subprocess.Popen(shlex.split(AndroidTool.adb_path + f"wait-for-device push {pq_file} sdcard/Movies/"),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            outs, errs = p.communicate(timeout=15)
            logging.info(outs.decode().strip('\n'))
            if errs:
                logging.error(errs.decode())
        except subprocess.TimeoutExpired:
            p.kill()
            logging.error("Timeout! Process killed!")

    @staticmethod
    def pause_resume_video():
        os.system("adb wait-for-device shell input keyevent 85")
        logging.info("adb wait-for-device shell input keyevent 85")

    @staticmethod
    def start_adb_log():
        file_name = "Android-Playback-"+time.asctime().replace(" ", "-")
        logging.debug('adb logcat -c')
        os.system('adb logcat -c')
        p = subprocess.Popen(shlex.split("adb logcat"), stdout=open("../log/%s.txt" % file_name, "w"), stderr=subprocess.STDOUT)
        return p

    @staticmethod
    def end_adb_log(logcat_p):
        logcat_p.terminate()
        logcat_p.kill()


@click.command()
@click.option("--path", prompt="Please input your MP4 folder location", default=os.getcwd(),
              help="Specify the results folder path. Default would be current location")
def main(path):
    file_path = "sdcard/Movies/"
    # AndroidTool.push_video(path, file_path)
    test_vector = AndroidTool.get_video_list_from_storage(file_path)
    json_location = os.getcwd()
    AndroidTool.write_json(test_vector, file_path, json_location)
    output = os.path.join(json_location, '../dolby.exolist.json')
    os.system(AndroidTool.adb_path + f"wait-for-device push {output} sdcard/Movies/")


if __name__ == "__main__":
    main()
    # p = AndroidTool.start_adb_log()
    # time.sleep(5)
    # AndroidTool.end_adb_log(p)
