import anthropic, os
client = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))
response = client.messages.create(model='claude-3-5-sonnet-latest', max_tokens=50, messages=[{'role': 'user', 'content': 'Say hello in exactly 5 words.'}])
print('✅ SUCCESS! Response:', response.content[0].text)
