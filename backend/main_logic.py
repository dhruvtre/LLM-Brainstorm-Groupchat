import anthropic
from openai import OpenAI
import json
import asyncio
import re
from pprint import pprint
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

Anthropic_key = os.getenv("Anthropic_key")
OpenAI_key = os.getenv("OpenAI_key")
OpenAIclient = OpenAI(api_key=OpenAI_key)
Anthropicclient = anthropic.Client(api_key=Anthropic_key)

from system_prompts import green_hat_system, white_hat_system, black_hat_system
from reflection_prompts import green_inner_voice_reflection_prompt, black_inner_voice_reflection_prompt, white_inner_voice_reflection_prompt

async def openai_call_message(hat_name, chat_transcript):
  system_prompt = ''
  #retrieiving the right system prompt
  if hat_name == "green_hat": 
    system_prompt = green_hat_system
  elif hat_name == "black_hat":
    system_prompt = black_hat_system
  elif hat_name == "white_hat": 
    system_prompt = white_hat_system
  else:
    return print("hat_name not found. only use 'green_hat', 'white_hat', or 'black_hat'.")
  
  #making the openai call
  response = OpenAIclient.chat.completions.create(
    model="chatgpt-4o-latest",
    messages=[{"role": "system", "content":system_prompt},
            {"role": "user", "content": chat_transcript}
    ]
  )
  #returning response
  response_string = response.choices[0].message.content
  return response_string


def extract_messages(gpt_response):
    # Using re.DOTALL to allow '.' to match newline characters
    match = re.search(r'(?<=####)(.*?)(?=####)', gpt_response, re.DOTALL)
    if match:
        extracted_text = match.group(0).strip()  # Using .strip() to remove any leading/trailing whitespace
        return extracted_text
    else: 
      return gpt_response
  

async def call_thread(green_hat_transcript, white_hat_transcript, black_hat_transcript):
  green_hat_response, white_hat_response, black_hat_response = await asyncio.gather(
    openai_call_message("green_hat", green_hat_transcript),
    openai_call_message("white_hat", white_hat_transcript),
    openai_call_message("black_hat", black_hat_transcript)
  )
  return green_hat_response, white_hat_response, black_hat_response


def generate_inner_voice(transcript, hat_name):

    
    if hat_name == "green_hat": 
       system_prompt = green_inner_voice_reflection_prompt
    elif hat_name == "white_hat":
       system_prompt = white_inner_voice_reflection_prompt
    elif hat_name == "black_hat":
       system_prompt = black_inner_voice_reflection_prompt
    else: 
       print("Inner voice system prompt assignment failed.")
    
    #making inner voice calls
    
    inner_voice_response = OpenAIclient.chat.completions.create(
    model="gpt-4-0125-preview",
    messages=[{"role": "system", "content":system_prompt},
            {"role": "user", "content": transcript}
    ]
  )
  #returning response
    inner_voice_response_string = inner_voice_response.choices[0].message.content
    return inner_voice_response_string


def extract_decision(inner_voice):
    # More flexible pattern to handle variations in formatting
    match = re.search(r'FINAL DECISION:\s*(SEND|NOT SEND)', inner_voice, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).upper()
    else:
        # Look for keywords as fallback
        if "NOT SEND" in inner_voice.upper():
            return "NOT SEND"
        elif "SEND" in inner_voice.upper():
            return "SEND"
        else:
            return "NOT SEND"  # Default fallback


async def generate_inner_voice_async(transcript, hat_name):
    return generate_inner_voice(transcript, hat_name)


async def process_agent_responses(agent_transcripts):
   green_hat_transcript = agent_transcripts["green_hat"]
   white_hat_transcript = agent_transcripts["white_hat"]
   black_hat_transcript = agent_transcripts["black_hat"]
   
   green_hat_response, white_hat_response, black_hat_response = await call_thread(
      green_hat_transcript=green_hat_transcript, 
      black_hat_transcript=black_hat_transcript, 
      white_hat_transcript=white_hat_transcript
   )
   
   messages = {
      "white_hat": "WHITE_HAT: " + extract_messages(white_hat_response),
      "green_hat": "GREEN_HAT: " + extract_messages(green_hat_response),
      "black_hat": "BLACK_HAT: " + extract_messages(black_hat_response),
   }
  
   # Generate inner voice transcripts
   inner_voice_transcripts = {
      "white_hat": white_hat_transcript + "NEW MESSAGE :" + messages["white_hat"],
      "green_hat": green_hat_transcript + "NEW MESSAGE :" + messages["green_hat"],
      "black_hat": black_hat_transcript + "NEW MESSAGE :" + messages["black_hat"]
   }

   # Call all inner voices concurrently
   inner_voice_tasks = [
      generate_inner_voice_async(inner_voice_transcripts[hat], hat)
      for hat in ["white_hat", "black_hat", "green_hat"]
   ]
   inner_voice_results = await asyncio.gather(*inner_voice_tasks)
   
   # Create inner_voice dictionary from results
   inner_voice = {
      "white_hat": inner_voice_results[0],
      "black_hat": inner_voice_results[1], 
      "green_hat": inner_voice_results[2]
   }
   
   # Extract decisions
   decisions = {
      hat: extract_decision(voice) for hat, voice in inner_voice.items()
   }
   
   # Build responses
   responses = [
      {
         "agent": hat,
         "message": messages[hat],
         "innerVoice": inner_voice[hat],
         "decision": decisions[hat]
      } for hat in messages.keys()
   ]
  
   return responses


def update_agent_transcripts(responses, agent_transcripts):
    # Group responses by agent
    responses_by_agent = {resp["agent"]: resp for resp in responses}
    
    # Update each agent's transcript individually
    for hat_name, transcript in agent_transcripts.items():
        # Add agent's own inner voice
        resp = responses_by_agent[hat_name]
        inner_voice_addition = f"NEW MESSAGE: {hat_name.upper()}: {resp['message']}\n"
        inner_voice_addition += f"INNER VOICE: {resp['innerVoice']}\n"
        
        # Add sent messages (including own if SEND, excluding if NOT SEND)
        sent_additions = ""
        for agent, agent_resp in responses_by_agent.items():
            if agent != hat_name and agent_resp["decision"] == "SEND": 
              sent_additions += f"{agent.upper()}: {agent_resp['message']}\n"
        
        # Update transcript
        agent_transcripts[hat_name] = transcript + inner_voice_addition + sent_additions
    
    return agent_transcripts





