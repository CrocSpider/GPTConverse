import whisper

model = whisper.load_model("tiny")
result = model.transcribe('C:\save\AI\GPTConverse\output.wav')
print(result["text"])