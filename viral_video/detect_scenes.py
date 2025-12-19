import os
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

def detect_scenes(video_path, threshold=30.0):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))

    video_manager.set_downscale_factor()
    video_manager.start()

    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()

    print(f"Found {len(scene_list)} scenes in {video_path}")
    for i, (start, end) in enumerate(scene_list):
        print(f"Scene {i+1}: Start {start.get_timecode()} - End {end.get_timecode()}")

    video_manager.release()
    return scene_list

if __name__ == "__main__":
    detect_scenes("NYC VLOG_ Day in the Life Exploring the City and Living my Best Life.mp4")
