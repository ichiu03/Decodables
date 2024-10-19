from openai import OpenAI
import unicodedata

#Merriam Webster Has Multiple Versions including ones specifically for kids
client = OpenAI(
    api_key = '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'
)



while True: 
    try:
        childage = input("What is the child's age: ")
        childage = int(childage)  
        break 
    except ValueError:
        print("Please input a number")

childage = str(childage)
#Gets the child age, verifies it is a number and then changes it back to a string so it can be concatenated

messages = [{
    "role": "system",
    "content": "You are a writer who creates engaging stories for special needs children of age " + childage + " with dyslexia. Only use the phoentic sounds specified."
     }]
#Gives Instructions to the system

def dyslexiaTest ():
    suitSounds = [
    '/s/', '/t/', '/b/', '/m/', '/l/', '/d/', '/n/', '/p/', '/k/', '/ʤ/', '/v/', '/z/', '/f/', '/k/', '/g/', '/r/', '/h/', '/w/', '/ks/', '/j/',
    '/æ/', '/eɪ/', '/ɪ/', '/aɪ/', '/ɒ/', '/oʊ/', '/ʌ/', '/uː/', '/ɛ/', '/iː/',
    '/fszl/', '/kw/', '/ʃ/', '/eɪ/', '/sk/', '/bl/', '/kl/', '/br/', '/kr/', '/k/', '/ʧ/', '/ɔː/', '/aɪ/',
    '/ɪə/', '/ə/', '/ɔː/', '/ɔː/', '/eɪ/', '/iː/', '/ɛ/', '/ɒr/', '/ɑːr/', '/ɜːr/', '/ɔɪ/',
    '/-li/', '/ɪŋ/', '/ʌŋ/', '/ɪd/', '/bl/', '/gl/', '/kl/',
    '/θ/', '/ʧ/', '/hw/', '/g/', '/n/', '/r/', '/m/', '/n/', '/aʊ/', '/oʊ/'
]
    allSounds = ''
    for i in range(len(suitSounds)):
        allSounds = allSounds + suitSounds[i] + ' and '  
    return allSounds


dyslexiaInf = "The story should only include the phoenetic sounds" + dyslexiaTest()
#Here we will intake dyslexia information and create a sort of check system

message = input("What do you want your story to be about: ")
finalprompt = "Generate me an engaging story about " + message + ". " + dyslexiaInf
messages.append({"role" : "user", "content": finalprompt})
#Provides the prompt and intakes the input the user provides into the message

chat = client.chat.completions.create(
    messages=messages,
    model="gpt-3.5-turbo",
)
reply = chat.choices[0].message.content
#Selects Chats first response, can be altered if we want to check which is best

print(reply)


#def story_call(finalprompt):
 #   return 0
# Implement some sort of checking system 
# Ideally could check over entire story, or go word by word. 
# If we can make word by word process be 10-20 ms runtime and entire book would be less than a second. 
# Here we should use the Merriam Webster dictionary to check phoenetics and possibly find synonms