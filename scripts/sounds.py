import pyaudio
import wave
import os

def play_audio(file_path):
    # 打开wav文件
    wf = wave.open(file_path, 'rb')
    # 初始化pyaudio
    p = pyaudio.PyAudio()
    # 打开音频流
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    # 读取数据并播放
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)


    # 停止和关闭流
    stream.stop_stream()
    stream.close()
    # 关闭pyaudio
    p.terminate()
    
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    play_audio(rf'{script_dir}\assets\success.wav')
