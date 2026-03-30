import platform
import psutil

##########################################################
# sound *BIG TODO HERE
##########################################################
try:
    if platform.system() == "Windows":
        # untested, since im on l00nix
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
        from comtypes import CLSCTX_ALL
        from ctypes import cast, POINTER
    elif platform.system() == "Linux":
        # THIS WILL BE DONE LATER ON IN CHOOSE AUDIO BACKEND
        pass

except ImportError as e:
    print(f"Missing library: {e}")
    exit("Install: pip install psutil pycaw (for windows) or pip install pulsectl (for linux)")

class VolumeControl:
    def __init__(self, app_name=None):
        self.system = platform.system()
        self.app_name = app_name or self._get_current_python_process_name()
        # l00nix specific
        self.audio_backend = self._choose_audio_backend()
        self.alsa_volume = None

    
    def _get_current_python_process_name(self):
        return psutil.Process().name()

    def _choose_audio_backend(self):    
        if self.system != "Linux":
            return None

        try:
            import alsaaudio
            return "alsa"
        except ImportError:            
            try:
                import pulsectl
                return "pulse"
            except ImportError:
                raise ImportError("No audio control library found. Install pulsectl or pyalsaaudio.")

    def set_volume(self, volume_level):
        # TODO: playback something async (maybe using a subprocess???) in order to adjust the volume accordingly

        # Normalize volume between 0.0 and 1.0
        volume_level = max(0.0, min(1.0, volume_level))

        if self.system == "Windows":
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.SimpleAudioVolume:
                    if session.Process.name().lower() == self.app_name.lower():
                        volume = session.SimpleAudioVolume
                        volume.SetMasterVolume(volume_level, None)
                        break

        elif self.system == "Linux":
            if self.audio_backend == None:
                print("Weird error. Audio backend not found")
                raise ImportError("No audio backend found. Install pulsectl or pyalsaaudio.")

            elif self.audio_backend == "pulse":
                import pulsectl
                with pulsectl.Pulse('volume-control') as pulse:
                    sink_inputs = pulse.sink_input_list()
                    for sink_input in sink_inputs:
                        app_name = sink_input.proplist.get('application.name', '').lower()
                        if self.app_name.lower() in app_name:
                            pulse.volume_set_all_chans(sink_input, volume_level)
                            break
            
            elif self.audio_backend == "alsa":
                import subprocess
                proc = subprocess.Popen('/usr/bin/amixer sset Master '+ str(round(volume_level * 100)) +'%', shell=True, stdout=subprocess.PIPE)
                proc.wait()
                # import alsaaudio
                # self.alsa_volume = volume_level
                # # ALSA mixer control (may require root/sudo)
                # mixer = alsaaudio.Mixer()
                # # Convert volume to ALSA scale (0-100)
                # alsa_volume = int(volume_level * 100)
                # mixer.setvolume(alsa_volume)

    def get_volume(self):
        if self.system == "Windows":
            from pycaw.pycaw import AudioUtilities
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.SimpleAudioVolume:
                    if session.Process.name().lower() == self.app_name.lower():
                        return session.SimpleAudioVolume.GetMasterVolume()

        elif self.system == "Linux":
            if self.audio_backend == None:
                print("Weird error. Audio backend not found")
                raise ImportError("No audio backend found. Install pulsectl or pyalsaaudio.")

            elif self.audio_backend == "pulse":
                
                with pulsectl.Pulse('volume-control') as pulse:
                    sink_inputs = pulse.sink_input_list()
                    for sink_input in sink_inputs:
                        app_name = sink_input.proplist.get('application.name', '').lower()
                        if self.app_name.lower() in app_name:
                            return sink_input.volume.values[0]
            
            elif self.audio_backend == "alsa":
                
                # ALSA mixer control
                mixer = alsaaudio.Mixer()
                # ALSA returns volume as 0-100 scale
                return mixer.getvolume()[0] / 100.0

        return None  # If no matching application or volume found

##########################################################
