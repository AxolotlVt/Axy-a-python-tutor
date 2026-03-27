# axy/ollama_client.py
# ==============================================================================
# Copyright (c) 2026 Axo. All rights reserved.
# 
# This software is proprietary and confidential.
# Unauthorized copying, distribution, modification, or use of this file,
# via any medium, is strictly prohibited without the express written 
# consent of the developer.
# 
# AXY - Local Python Mentor
# ==============================================================================
import requests
import time
import json  # for pretty error printing
import logging

logger = logging.getLogger(__name__)

URL = "http://127.0.0.1:11434/api/chat"  # Changed to 127.0.0.1 for Windows reliability


def ask_ollama(messages, model="phi3", temperature=0.5):
    """Send a chat request to the local Ollama server.

    The function behaves as a generator so callers can iterate over the
    response as it streams back from the model.  If the streaming endpoint
    fails or produces no content we fall back to a normal (non‑streaming)
    request but **make sure** to yield the resulting text instead of
    returning it.  The previous implementation returned the fallback value
    which is swallowed by the caller and caused "missing" answers.
    """

    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_ctx": 4069,
            "num_predict": 1024,
            "num_gpu": 99,
            "num_thread": 4,
        },
    }

    yielded_any = False
    try:
        # Usamos stream=True en requests para no esperar todo el bloque
        with requests.post(URL, json=payload, stream=True, timeout=180) as r:
            r.raise_for_status()

            for line in r.iter_lines():
                if line:
                    try:
                        # Ollama manda JSONs línea por línea
                        chunk = json.loads(line.decode("utf-8"))
                        # Extraemos el pedacito de texto
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yielded_any = True
                            yield content  # <--- ENTREGAMOS LA GOTA DE TEXTO
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        logger.exception("Error calling Ollama: %s", e)
        yield f"[Error: {str(e)}]"

    # if the streaming request never produced anything we try a normal call
    if not yielded_any:
        for attempt in range(3):
            try:
                logger.debug("Sending fallback request to %s (attempt %d)", URL, attempt + 1)
                r = requests.post(URL, json=payload, timeout=180)
                r.raise_for_status()
                logger.debug("Fallback success: status=%s", r.status_code)
                result_content = r.json()["message"]["content"]
                # yield the text so the caller actually receives it
                yield result_content
                return
            except requests.exceptions.ConnectionError as e:
                logger.debug("Connection failed: %s", e)
                if attempt == 0:
                    logger.info("Waiting for Ollama to start...")
                time.sleep(3)
            except requests.exceptions.HTTPError as e:
                logger.warning("Ollama HTTP error %s: %s", r.status_code, r.text)
                yield f"[Ollama HTTP error {r.status_code}: {r.text}]"
                return
            except Exception as e:
                logger.exception("Unexpected error when calling Ollama: %s", e)
                yield f"[Ollama error: {e}]"
                return

        yield "I'm having trouble connecting to Ollama right now. Can you run 'ollama serve' in another terminal?"