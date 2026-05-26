# ============================================================
# JARVIS Startup Sound (generated in Python, no asset files)
# ============================================================

import io
import math
import struct
import wave


def generate_startup_wav_bytes(duration=0.8, sample_rate=44100):
    """Build WAV audio bytes entirely in memory."""
    frames = []
    for i in range(int(duration * sample_rate)):
        t = i / sample_rate
        freq = 440 + 200 * math.sin(t * 8)
        value = int(32767 * 0.4 * math.sin(2 * math.pi * freq * t) * math.exp(-t * 2))
        frames.append(struct.pack("<h", value))

    buffer = io.BytesIO()
    with wave.open(buffer, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(frames))
    buffer.seek(0)
    return buffer.read()


def play_startup_sound():
    """Play startup tone using only Python (pygame or winsound)."""
    wav_bytes = generate_startup_wav_bytes()

    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.Sound(io.BytesIO(wav_bytes)).play()
        return
    except Exception:
        pass

    try:
        import tempfile
        import os
        import winsound

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav_bytes)
            path = tmp.name
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        try:
            os.remove(path)
        except OSError:
            pass
    except Exception:
        try:
            import winsound
            winsound.Beep(880, 300)
            winsound.Beep(1100, 200)
        except Exception:
            pass
