from dlb_dvision_utils.plugins.mediainfo import AddHandler


class Video:
    def __init__(self, test_vector):
        '''
        :param test_vector: path to the test vector
        '''
        # PWT-hevc_sdr_10b-FHD-MP4-59_94
        handler = AddHandler(test_vector)
        video_file = handler.analyze_video_file()
        self.video_info = video_file.to_data()

    def get_video_length(self):
        return int(str(self.video_info['duration'])[:2])

    def get_video_fps(self):
        return self.video_info['frame_rate']

    def get_video_resolution(self):
        return "x".join([str(self.get_video_width()), str(self.get_video_height())])

    def get_video_width(self):
        return self.video_info['width']

    def get_video_height(self):
        return self.video_info['height']

    @staticmethod
    def is_file_video(filename):
        if filename.lower().endswith(".mp4") or filename.lower().endswith(".mov") or filename.lower().endswith(".m4v"):
            return True
        return False
