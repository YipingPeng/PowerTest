import os
import re
import subprocess
import shlex
import logging
import time
from video_tool import Video


class IOSTool:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    @staticmethod
    def is_phone_connected():
        cmd = "idevice_id"
        ret_out = subprocess.check_output(shlex.split(cmd), shell=False, ).decode()
        if ret_out:
            return True
        else:
            return False

    @staticmethod
    def push_file(i_path, o_path):
        cmd = f"cp {i_path} {o_path}"
        logging.info("Executing: " + cmd)
        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

    @staticmethod
    def get_device_os_version():
        cmd = "ideviceinfo -k ProductVersion"
        output = subprocess.check_output(cmd.split(" "), shell=False).decode().splitlines()[-1]

        return output

    @staticmethod
    def get_udid():
        return subprocess.check_output("idevice_id", shell=False).decode().splitlines()[-1].split(" ")[0]

    @staticmethod
    def get_device_name():
        return re.findall(r"DeviceName:\s.+", subprocess.check_output("ideviceinfo", shell=False).decode())[0].split(":")[-1][1:]

    @staticmethod
    def mount_image():
        ios_version = IOSTool.get_device_os_version()
        os.system(
            f"ideviceimagemounter -d /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform"
            f"/DeviceSupport/{ios_version}/DeveloperDiskImage.dmg "
            f"/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/DeviceSupport/"
            f"{ios_version}/DeveloperDiskImage.dmg.signature")

    @staticmethod
    def mount_app(bundle_id, folder_name):
        os.system(f'ifuse --documents {bundle_id} {folder_name}')

    @staticmethod
    def umount_app(folder_name):
        os.system(f'umount -f {folder_name}')

    @staticmethod
    def run_ios_unit_test_app(bundle_id="com.dolby.ios-unit-test"):
        os.system(f'idevicedebug run {bundle_id}')

    @staticmethod
    def kill_ios_unit_test_app(bundle_id="com.dolby.ios-unit-test"):
        os.system(f'idevicedebug kill {bundle_id}')

    @staticmethod
    def write_objective_test_cfg(width, height, bitdepth, input_yuv, input_cm, input_dm):
        with open("TestConfig.txt", "w") as file:
            file.write(f"""VERBOSE 0
    TEST_MODE 1
    OUTPUT_FOLDER_PATH ./
    NUM_INPUT_FRAMES 1
    TEST_ID 4
    BL_CCID 4
    DOVI_CONFIG_FILE /dolby_vision.cfg
    INPUT_BL_0 /{input_yuv}
    INPUT_COMP_BIN_0 /{input_cm}
    INPUT_DM_BIN_0 /{input_dm}

    WIDTH {width}
    HEIGHT {height}
    BL_BIT_DEPTH {bitdepth}
    FRAME_FORMAT 444""")
        file.close()

    @staticmethod
    def push_video(i_path, o_path):
        for root, dirs, files, in os.walk(i_path):
            for file in files:
                if Video.is_file_video(file) and file not in os.listdir(o_path):
                    cmd = f"cp {os.path.join(root, file)} {o_path}"
                    logging.info("Executing: " + cmd)
                    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    p.wait()

    @staticmethod
    def change_mode(pq_file, o_path, low_power_mode=1):
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

        logging.info(f"Executing: cp {pq_file} {o_path}")
        p = subprocess.Popen(shlex.split(f"cp {pq_file} {o_path}"),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            outs, errs = p.communicate(timeout=15)
            if outs:
                logging.info(outs.decode().strip('\n'))
            if errs:
                logging.error(errs.decode())
        except subprocess.TimeoutExpired:
            p.kill()
            logging.error("Timeout! Process killed!")

    @staticmethod
    def get_log():
        file_name = "iOS-Playback-" + time.asctime().replace(" ", "-")
        return subprocess.Popen(shlex.split("idevicesyslog -p DvDecodingApp -> ../log/%s.txt" % file_name), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @staticmethod
    def end_log(log_p):
        log_p.terminate()
        log_p.kill()

