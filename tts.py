from gtts import gTTS
from playsound import playsound

tts = gTTS(text='Zück zück, ich bin im Gommemowd, hehe!', lang='de', slow=False)
tts.save('tts.mp3')
playsound('tts.mp3')