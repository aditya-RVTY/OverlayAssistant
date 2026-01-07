import base64
from io import BytesIO
from openai import OpenAI
import ollama
from overlay_ai.utils.config import OPENAI_API_KEY, AI_PROVIDER, OLLAMA_MODEL, LLAMA_MODEL_PATH, LLAMA_CLIP_PATH, LLAMA_N_GPU_LAYERS

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def encode_image(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def image_to_bytes(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    return buffered.getvalue()

llama_instance = None

def init_llama():
    global llama_instance
    if llama_instance: return
    
    try:
        from llama_cpp import Llama
        from llama_cpp.llama_chat_format import Llava15ChatHandler
    except ImportError:
        print("Error: llama-cpp-python not installed. Run `pip install llama-cpp-python`.")
        return

    print("Loading Llama.cpp model... (This may take a moment)")
    
    chat_handler = None
    if LLAMA_CLIP_PATH:
        chat_handler = Llava15ChatHandler(clip_model_path=LLAMA_CLIP_PATH)
    
    llama_instance = Llama(
        model_path=LLAMA_MODEL_PATH,
        chat_handler=chat_handler,
        n_gpu_layers=LLAMA_N_GPU_LAYERS,
        n_ctx=2048, # Adjust context window as needed
        verbose=True
    )

def verify_response_quality(user_text, response_text, image=None, ocr_text="", manual_context="", history=None):
    """
    Uses the AI to critique the response. 
    Returns (is_valid: bool, critique: str)
    """
    verification_prompt = (
        f"You are a Quality Assurance AI. \n"
        f"User asked: '{user_text}'\n"
        f"Assistant Answered: '{response_text}'\n"
        f"Context provided: OCR='{ocr_text[:100]}...', Manual='{manual_context[:100]}...'\n\n"
        f"Task: Evaluate the Assistant's answer.\n"
        f"1. Is it relevant to the user's question?\n"
        f"2. Is it coherent (not garbage)?\n"
        f"3. If Image/OCR was involved, does it seem grounded?\n\n"
        f"Reply strictly in this format:\n"
        f"PASS\n"
        f"(or)\n"
        f"FAIL: <Short Reason>"
    )
    
    # We use the same provider for verification to keep it simple
    # We strip image for verification to save bandwidth/speed, unless critical?
    # Actually, verification needs context. But 'Critic' usually works on text logic.
    # Let's try text-only verification first for speed.
    
    critique = query_assistant_raw(verification_prompt, image=None, history=None)
    
    if "PASS" in critique.upper():
        return True, ""
    else:
        return False, critique

def query_assistant_raw(prompt, image=None, ocr_text="", manual_context="", history=None):
    """
    Helper to call the current provider directly without recursion/loops of verification.
    """
    if AI_PROVIDER == "ollama":
        return query_ollama(prompt, image, ocr_text, manual_context, history)
    elif AI_PROVIDER == "llamacpp":
        return query_llamacpp(prompt, image, ocr_text, manual_context, history)
    else:
        return query_openai(prompt, image, ocr_text, manual_context, history)

def query_assistant(user_text, image=None, ocr_text="", manual_context="", history=None):
    """
    Main dispatcher with Verification Loop.
    """
    # 1. Generate Draft
    draft_response = query_assistant_raw(user_text, image, ocr_text, manual_context, history)
    
    # 2. Verify
    is_valid, reason = verify_response_quality(user_text, draft_response, image, ocr_text, manual_context, history)
    
    if is_valid:
        return draft_response
    else:
        print(f"Verification Failed: {reason}. Retrying...")
        # 3. Retry (Once)
        retry_prompt = (
            f"Your previous answer was rejected by QA.\n"
            f"User Question: {user_text}\n"
            f"Rejected Answer: {draft_response}\n"
            f"QA Reason: {reason}\n\n"
            f"Please allow me to try again. Provide a better, accurate answer."
        )
        
        # We append this to history temporarily for the retry? Or just send as prompt?
        # Sending as new prompt is cleaner for one-shot retry.
        retry_response = query_assistant_raw(retry_prompt, image, ocr_text, manual_context, history)
        
        # We could verify again, but let's avoid infinite loops. Return the retry.
        return f"{retry_response}\n\n[Note: Initial response was flagged by Quality Agent and regenerated.]"

# ... (query_openai remains same) ...

def query_llamacpp(user_text, image=None, ocr_text="", manual_context="", history=None):
    init_llama()
    if not llama_instance:
        return "Error: Llama model failed to load. Check console/logs."

    # Construct Prompt
    full_prompt = f"{user_text}"
    if ocr_text:
        full_prompt += f"\n\n[System OCR]:\n{ocr_text}"
    if manual_context:
        full_prompt += f"\n\n[Manual Context]:\n{manual_context}"
    
    messages = []
    if history:
        messages.extend(history)
    
    messages.append({"role": "user", "content": full_prompt})
    
    # Handle Image
    # llama-cpp-python expected message format for vision:
    # {"role": "user", "content": [ {"type": "text", "text": "..."}, {"type": "image_url", "image_url": "data:image/jpeg;base64,..."} ]}
    if image:
        # We need to restructure the last message for multimodal
        base64_img = encode_image(image)
        content_list = [
            {"type": "text", "text": full_prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
        ]
        messages[-1]["content"] = content_list

    try:
        response = llama_instance.create_chat_completion(
            messages=messages,
            max_tokens=500
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Llama Error: {e}"

def query_openai(user_text, image=None, ocr_text="", manual_context="", history=None):
    if not client:
        return "Error: OpenAI API Key not configured."

    system_prompt = (
        "You are an intelligent overlay assistant. "
        "You see what the user sees on their screen. "
        "Use the provided screenshot, OCR text, manual context, and conversation history to answer the user's question. "
        "Be concise, helpful, and direct. "
        "If the user asks about the app they are using, guide them step by step."
    )

    messages = [{"role": "system", "content": system_prompt}]
    
    if history:
        messages.extend(history)

    user_content = [{"type": "text", "text": user_text}]
    
    if ocr_text:
        user_content.append({"type": "text", "text": f"\n[System OCR]:\n{ocr_text}"})
    if manual_context:
        user_content.append({"type": "text", "text": f"\n[Manual Context]:\n{manual_context}"})
    if image:
        base64_image = encode_image(image)
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
        })

    messages.append({"role": "user", "content": user_content})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {e}"

def query_ollama(user_text, image=None, ocr_text="", manual_context="", history=None):
    # Construct Plain Text Prompt
    full_prompt = f"{user_text}"
    if ocr_text:
        full_prompt += f"\n\n[System OCR]:\n{ocr_text}"
    if manual_context:
        full_prompt += f"\n\n[Manual Context]:\n{manual_context}"
    
    # Message History handling for Ollama
    # Ollama 'chat' API supports history list similar to OpenAI
    messages = []
    if history:
        # Convert history format if needed, but standard role/content works
        messages.extend(history)
    
    messages.append({"role": "user", "content": full_prompt, "images": []})
    
    # Handle Image
    if image:
        img_bytes = image_to_bytes(image)
        # Ollama python lib expects 'images' field in the message dict
        messages[-1]["images"] = [img_bytes]

    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"Ollama Error: {e}. Ensure Ollama is running (`ollama serve`)."
