from enum import Enum
import os
from playsound import playsound

sound_pack: str = "default"

class AudioFile(Enum):
    START = "start"
    SCAN_BLOCKS = "scan-blocks"
    SCAN_SHADOW = "scan-shadow"
    SOLVE_START = "solve-start"
    SOLVE_END = "solve-end"
    MOVE_BLOCKS = "move-blocks"
    FINISH = "finish"


def set_sound_pack(sound_folder: str) -> None:
    global sound_pack
    sound_pack = sound_folder

def play(audio_file: AudioFile) -> None:
    import main
    if(main.play_sound()):
        file = f"resources/audio/{sound_pack}/{audio_file.value}.mp3"
        if(os.path.exists(file)):
            playsound(sound=file, block=False)
