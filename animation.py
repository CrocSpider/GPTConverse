<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT Voice Web App</title>
</head>
<body>
    <h1>ChatGPT Voice Web App</h1>
    <form action="/process_voice" method="post">
        <label for="voiceInput">Enter voice input:</label>
        <input type="text" name="voiceInput" required>
        <button type="submit">Submit</button>
    </form>
    {% if chatgpt_response %}
        <p>ChatGPT Response: {{ chatgpt_response }}</p>
    {% endif %}
</body>
</html>
