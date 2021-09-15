"""
Given a directory of video files, play them randomly each for a given amount of time,
looping the video if necessary to reach the desired play time.
"""
import argparse
import os
import time
import random
import cv2


DEFAULT_LENGTH = 60 * .5  # default to 30-second videos

ACCEPTED_FORMATS = ['.mp4']

ESC_KEY = 27
ENTER_KEYS = [ord('\n'), ord('\r')]


def valid_dir(path):
    # validate a directory for argparse argument
    if os.path.isdir(path):
        return path
    else:
        raise NotADirectoryError(path)


def play_videos(directory, video_length=DEFAULT_LENGTH, accepted_formats=None):
    # make sure accepted_formats is a list of string formats
    if not accepted_formats:
        accepted_formats = ACCEPTED_FORMATS
    if isinstance(accepted_formats, str):
        accepted_formats = list(accepted_formats)
    # init variables
    is_closed = False
    cap = None
    all_videos = []
    # get the filepaths for all relevant videos in the directory recursively
    for subdir, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in files:
            filepath = subdir + os.sep + filename
            if any([filepath.endswith(_format) for _format in accepted_formats]):
                all_videos.append(filepath)

    print(f'Found {len(all_videos)} videos.')

    try:
        # loop forever randomly over our videos list
        while not is_closed:
            # randomly pick a video
            filepath = random.choice(all_videos)
            video_start = time.time()
            cap = cv2.VideoCapture(filepath)
            fps = cap.get(cv2.CAP_PROP_FPS)
            _start = time.time()
            # play the video until we reach the minimum video length
            while not is_closed:
                if (time.time() - video_start) > video_length:
                    break
                # read the next video frame
                ret, frame = cap.read()
                _end = time.time()
                # wait for our maximum fps (the fps detected from the video) so we don't play too quickly
                while (_end - _start) < 1/fps:
                    time.sleep(0.001)
                    _end = time.time()
                # show the frame if there was one
                if ret:
                    cv2.imshow('frame', frame)
                    _start = time.time()
                    keypress = cv2.waitKey(1)
                    if keypress is ESC_KEY:
                        # When esc is pressed, exit
                        is_closed = True
                        break
                    elif keypress in ENTER_KEYS:
                        # just go to next video if enter is pressed
                        break
                else:
                    # otherwise if there was no frame, set the video to the beginning and continue
                    cap.set(1, 0)
                    _start = time.time()
            cap.release()
    # final catch-all cleanup
    finally:
        if cap:
            cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('videos', help='Folder of videos to play', type=valid_dir)
    args = parser.parse_args()
    play_videos(args.videos)
