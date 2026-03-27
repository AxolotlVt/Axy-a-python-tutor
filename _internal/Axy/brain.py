# axy/brain.py
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
from .ollama_client import ask_ollama
from .personality import get_system_prompt
from .mastery_system import MasterySystem, get_mastery_system
from .code_analyzer import analyze_and_correct_code, analyze_code_performance
from .paths import get_chat_history_path
import json
import os
import logging
import re
import hashlib
import random
import unicodedata
from typing import Optional, Dict

logger = logging.getLogger(__name__)

ACADEMIC_DISHONESTY_PATTERNS = (
    r"\b(?:do|complete|finish|solve|write|make)\b.{0,40}\b(?:my\s+)?(?:homework|assignment|essay|exam|quiz|test|lab|project)\b",
    r"\b(?:homework|assignment|essay|exam|quiz|test|lab|project)\b.{0,40}\b(?:for\s+me|without\s+explanation|just\s+the\s+answer|only\s+the\s+answer|answer\s+key|for\s+submission|to\s+submit)\b",
    r"\b(?:haz|hazme|resuelve|completa|termina|escribe)\b.{0,40}\b(?:mi\s+)?(?:tarea|deber|ensayo|examen|quiz|prueba|laboratorio|proyecto)\b",
    r"\b(?:tarea|deber|ensayo|examen|quiz|prueba|laboratorio|proyecto)\b.{0,40}\b(?:por\s+mi|sin\s+explicacion|solo\s+la\s+respuesta|para\s+entregar|para\s+copiar)\b",
    r"\b(?:plagiarism|plagiarize|plagiarise|plagio)\b",
    r"\b(?:turnitin|proctorio|lockdown\s+browser|plagiarism\s+detector)\b.{0,20}\b(?:bypass|avoid|evade|skip)\b",
    r"\b(?:cheat|cheating|copiar|hacer\s+trampa)\b.{0,20}\b(?:exam|quiz|test|homework|assignment|examen|quiz|prueba|tarea)\b",
    r"\b(?:exam|quiz|test|homework|assignment|examen|quiz|prueba|tarea)\b.{0,20}\b(?:cheat|cheating|copiar|hacer\s+trampa)\b",
)

MALICIOUS_OR_UNETHICAL_PATTERNS = (
    r"\b(?:malware|virus|trojan|ransomware|worm|spyware|keylogger|rootkit|botnet|backdoor|rat)\b",
    r"\b(?:steal|exfiltrate|dump|harvest|robar|extraer)\b.{0,30}\b(?:passwords?|tokens?|cookies?|credentials?|data|contrasenas?|credenciales|datos)\b",
    r"\b(?:phish|phishing|spoof|credential\s+harvest)\b",
    r"\b(?:ddos|dos|bruteforce|brute\s+force|sql\s*injection|xss|csrf|bypass\s+auth|privilege\s+escalation)\b",
    r"\b(?:hack|compromise|infect|deploy)\b.{0,25}\b(?:system|computer|server|account|device|wifi|router|email|instagram|facebook|whatsapp|cuenta|correo)\b",
    r"\b(?:spy\s+on|stalk|doxx|harass|blackmail|impersonate)\b",
    r"\b(?:fake\s+id|forgery|counterfeit|forjar|documento\s+falso)\b",
)

TOPIC_KEYWORDS = {
    "binary search": ("algorithms", "searching", 175),
    "data type": ("fundamentals", "variables", 50),
    "arraylist": ("fundamentals", "lists", 75),
    "quicksort": ("algorithms", "sorting", 200),
    "mergesort": ("algorithms", "sorting", 200),
    "base case": ("algorithms", "recursion", 175),
    "linked": ("data_structures", "linked_lists", 250),
    "dictionary": ("data_structures", "dictionaries", 150),
    "dictionaries": ("data_structures", "dictionaries", 150),
    "diccionario": ("data_structures", "dictionaries", 150),
    "hashmap": ("data_structures", "dictionaries", 150),
    "hashtable": ("data_structures", "dictionaries", 150),
    "conjunto": ("data_structures", "sets", 150),
    "hashset": ("data_structures", "sets", 150),
    "ordenamiento": ("algorithms", "sorting", 200),
    "recursion": ("algorithms", "recursion", 175),
    "recursiva": ("algorithms", "recursion", 175),
    "recursive": ("algorithms", "recursion", 175),
    "busqueda": ("algorithms", "searching", 175),
    "search": ("algorithms", "searching", 175),
    "ordenar": ("algorithms", "sorting", 200),
    "sorting": ("algorithms", "sorting", 200),
    "grafo": ("algorithms", "graphs", 250),
    "graph": ("algorithms", "graphs", 250),
    "vertex": ("algorithms", "graphs", 250),
    "edge": ("algorithms", "graphs", 250),
    "dfs": ("algorithms", "graphs", 250),
    "bfs": ("algorithms", "graphs", 250),
    "variables": ("fundamentals", "variables", 50),
    "variable": ("fundamentals", "variables", 50),
    "tipo": ("fundamentals", "variables", 50),
    "int": ("fundamentals", "variables", 50),
    "string": ("fundamentals", "variables", 50),
    "boolean": ("fundamentals", "variables", 50),
    "listas": ("fundamentals", "lists", 75),
    "lista": ("fundamentals", "lists", 75),
    "list": ("fundamentals", "lists", 75),
    "array": ("fundamentals", "lists", 75),
    "vector": ("fundamentals", "lists", 75),
    "bucles": ("fundamentals", "loops", 100),
    "bucle": ("fundamentals", "loops", 100),
    "loop": ("fundamentals", "loops", 100),
    "loops": ("fundamentals", "loops", 100),
    "while": ("fundamentals", "loops", 100),
    "foreach": ("fundamentals", "loops", 100),
    "iteration": ("fundamentals", "loops", 100),
    "funciones": ("fundamentals", "functions", 125),
    "funcion": ("fundamentals", "functions", 125),
    "function": ("fundamentals", "functions", 125),
    "functions": ("fundamentals", "functions", 125),
    "method": ("fundamentals", "functions", 125),
    "def ": ("fundamentals", "functions", 125),
    "void": ("fundamentals", "functions", 125),
    "procedure": ("fundamentals", "functions", 125),
    "dict": ("data_structures", "dictionaries", 150),
    "sets": ("data_structures", "sets", 150),
    "tuplas": ("data_structures", "tuples", 125),
    "tupla": ("data_structures", "tuples", 125),
    "tuple": ("data_structures", "tuples", 125),
    "struct": ("data_structures", "tuples", 125),
    "nodo": ("data_structures", "linked_lists", 250),
    "node": ("data_structures", "linked_lists", 250),
    "sort": ("algorithms", "sorting", 200),
    "bubble": ("algorithms", "sorting", 200),
    "graphs": ("algorithms", "graphs", 250),
    "clases": ("advanced", "oop", 700),
    "inheritance": ("advanced", "oop", 700),
    "herencia": ("advanced", "oop", 700),
    "interface": ("advanced", "oop", 700),
    "polymorphism": ("advanced", "oop", 700),
    "encapsulation": ("advanced", "oop", 700),
    "decorator": ("advanced", "decorators", 600),
    "wrapper": ("advanced", "decorators", 600),
    "annotation": ("advanced", "decorators", 600),
    "attribute": ("advanced", "decorators", 600),
    "generator": ("advanced", "generators", 550),
    "iterator": ("advanced", "generators", 550),
    "yield": ("advanced", "generators", 550),
    "enumerable": ("advanced", "generators", 550),
    "async": ("advanced", "async", 800),
    "asincrona": ("advanced", "async", 800),
    "concurrent": ("advanced", "async", 800),
    "future": ("advanced", "async", 800),
    "promise": ("advanced", "async", 800),
    "coroutine": ("advanced", "async", 800),
    "thread": ("advanced", "async", 800),
}

class Axy:
    def __init__(self, model="Qwen-2.5-Coder:1.5B", history=None, user_data=None, save_callback=None):
        self.model = model
        self.user_data = user_data or {}
        self.save_callback = save_callback
        self.mastery = MasterySystem(user_data=self.user_data, save_callback=self.save_callback)
        self.history = self._load_smart_history()
        self.recent_awarded_questions = set()  # Track recent questions that earned points
        self.messages_since_last_test = 0  # Counter for triggering tests
        self.pending_test = None  # Store pending test data
        
        # Inject system prompt only if not already there
        if not any(m["role"] == "system" for m in self.history):
            system_content = get_system_prompt()
            # If there's existing conversation history, add a context reminder
            non_system_messages = [m for m in self.history if m["role"] != "system"]
            if len(non_system_messages) > 2:
                system_content += f"\n\n[CONTEXT: We have had {len(non_system_messages)} messages in our conversation. Continue from where we left off naturally.]"
            self.history.insert(0, {"role": "system", "content": system_content})

    def _get_history_path(self):
        return str(get_chat_history_path())

    def _load_smart_history(self):
        path = self._get_history_path()
        if not os.path.exists(path): return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                full_history = json.load(f)

            # SPACE MANAGEMENT: Keep only recent messages to prevent disk bloat
            # Load up to 50 recent messages for context, but enforce total limit
            max_messages = 50
            non_system_messages = [m for m in full_history if m["role"] != "system"]
            
            # If history is too large, keep only the most recent messages
            if len(non_system_messages) > max_messages:
                # Keep the last max_messages messages
                recent_messages = non_system_messages[-max_messages:]
                # Reconstruct full history with system message + recent messages
                system_messages = [m for m in full_history if m["role"] == "system"]
                if system_messages:
                    return system_messages + recent_messages
                return recent_messages
            
            return full_history
        except Exception as e:
            logger.warning("Failed to load history: %s", e)
            return []

    def _save_full_history(self):
        path = self._get_history_path()
        savable = [msg for msg in self.history if msg["role"] != "system"]
        try:
            # Ensure target directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # SPACE MANAGEMENT: Check disk usage before saving
            from .space_manager import space_manager
            space_info = space_manager.check_space_usage()
            if space_info["needs_cleanup"]:
                logger.warning(f"High disk usage detected ({space_info['usage_percent']}%), running cleanup")
                cleanup_stats = space_manager.cleanup_old_data()
                logger.info(f"Cleanup completed: {cleanup_stats}")

            # Write atomically: write to a temp file in the same directory then replace
            tmp_path = path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(savable, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, path)
        except Exception as e:
            logger.warning("Could not save history: %s", e)

    def _detect_language(self, text: str) -> str:
        """
        Detecta si el texto está en español o inglés.
        Biased heavily towards conversation history for CONSISTENCY.
        """
        # FIRST: Check if we've already established a language in conversation
        # Once a language is set, STICK WITH IT (unless explicitly broken)
        user_messages = [msg for msg in self.history if msg.get('role') == 'user']
        
        # If we have 3+ messages in the conversation, lock to the conversation language
        if len(user_messages) >= 3:
            conversation_lang = self._get_conversation_language()
            if conversation_lang:
                return conversation_lang
        
        # Otherwise, detect from the current message
        spanish_markers = ["hola", "que", "de", "para", "español", "ya", "entendí", "entendi", "está", "esta", "funciona", "¿", "¡"]
        english_markers = ["hello", "what", "how", "english", "works", "thank"]
        
        text_lower = text.lower()
        spanish_score = sum(1 for marker in spanish_markers if marker in text_lower)
        english_score = sum(1 for marker in english_markers if marker in text_lower)
        
        return 'es' if spanish_score > english_score else 'en'
    
    def _get_conversation_language(self) -> str:
        """Determine the STRONGEST language of the conversation - gives immediate lock-in."""
        user_messages = [msg for msg in self.history if msg.get('role') == 'user']
        if not user_messages:
            return None
        
        # Use LAST message as the strongest signal
        last_msg = user_messages[-1].get('content', '')
        detected = self._detect_language_simple(last_msg)
        
        # If we have 2+ messages with consistent language, lock it in
        if len(user_messages) >= 2:
            last_two = [self._detect_language_simple(m.get('content', '')) for m in user_messages[-2:]]
            if last_two[0] == last_two[1]:
                return last_two[0]
        
        return detected
    
    def _detect_language_simple(self, text: str) -> str:
        """Quick language detection with improved markers."""
        text_lower = text.lower()
        
        # Strong Spanish indicators (common words that appear frequently in Spanish)
        spanish_strong = ["hola", "entendí", "entendi", "gracias", "por favor", "sí", "si ", "no ", "está", "qué", "cómo", "dónde", "cuándo", "porque", "porqué"]
        
        # Strong English indicators  
        english_strong = ["hello", "thank you", "please", "yes", "how", "what", "where", "when", "because", "ok", "okay"]
        
        # General programming terms (don't weight as heavily)
        programming_neutral = ["function", "loop", "class", "def ", "return", "variable", "array", "bucle", "función"]
        
        spanish_hits = sum(2 if m in text_lower else 0 for m in spanish_strong)
        english_hits = sum(2 if m in text_lower else 0 for m in english_strong)
        
        # Fallback to general markers if no strong indicators
        if spanish_hits == 0 and english_hits == 0:
            spanish_general = ["que", "de ", "para ", "español", "ya", "está", "esta", "funciona", "¡", "¿"]
            english_general = ["hello", "what", "how", "works", "english"]
            spanish_hits = sum(1 for m in spanish_general if m in text_lower)
            english_hits = sum(1 for m in english_general if m in text_lower)
        
        return 'es' if spanish_hits > english_hits else 'en'

    def _normalize_text(self, text: str) -> str:
        """Lowercase text and strip accents for more reliable keyword matching."""
        normalized = unicodedata.normalize("NFKD", text or "")
        return normalized.encode("ascii", "ignore").decode("ascii").lower()

    def _detect_topic_from_text(self, text: str) -> Optional[tuple]:
        """Detect a mastery topic from a single text snippet."""
        normalized_text = self._normalize_text(text)
        if not normalized_text:
            return None

        for keyword in sorted(TOPIC_KEYWORDS, key=len, reverse=True):
            clean_keyword = keyword.strip()
            pattern = r"\b" + re.escape(clean_keyword) + r"\b"
            if re.search(pattern, normalized_text):
                return TOPIC_KEYWORDS[keyword]

        return None

    def _infer_topic_from_history(self) -> Optional[tuple]:
        """
        Infer the topic being discussed from recent conversation history.
        Returns (category, topic, base_points) if found, else None.
        """
        topic_mapping = {
            "variable": ("fundamentals", "variables", 50),
            "tipo": ("fundamentals", "variables", 50),
            "data type": ("fundamentals", "variables", 50),
            "int": ("fundamentals", "variables", 50),
            "string": ("fundamentals", "variables", 50),
            "boolean": ("fundamentals", "variables", 50),
            "lista": ("fundamentals", "lists", 75),
            "list": ("fundamentals", "lists", 75),
            "array": ("fundamentals", "lists", 75),
            "vector": ("fundamentals", "lists", 75),
            "arraylist": ("fundamentals", "lists", 75),
            "bucle": ("fundamentals", "loops", 100),
            "loop": ("fundamentals", "loops", 100),
            "for": ("fundamentals", "loops", 100),
            "while": ("fundamentals", "loops", 100),
            "foreach": ("fundamentals", "loops", 100),
            "iteration": ("fundamentals", "loops", 100),
            "función": ("fundamentals", "functions", 125),
            "function": ("fundamentals", "functions", 125),
            "method": ("fundamentals", "functions", 125),
            "def ": ("fundamentals", "functions", 125),
            "void": ("fundamentals", "functions", 125),
            "return": ("fundamentals", "functions", 125),
            "procedure": ("fundamentals", "functions", 125),
            "diccionario": ("data_structures", "dictionaries", 150),
            "dictionary": ("data_structures", "dictionaries", 150),
            "dict": ("data_structures", "dictionaries", 150),
            "hashmap": ("data_structures", "dictionaries", 150),
            "hashtable": ("data_structures", "dictionaries", 150),
            "map": ("data_structures", "dictionaries", 150),
            "conjunto": ("data_structures", "sets", 150),
            "set": ("data_structures", "sets", 150),
            "hashset": ("data_structures", "sets", 150),
            "tupla": ("data_structures", "tuples", 125),
            "tuple": ("data_structures", "tuples", 125),
            "struct": ("data_structures", "tuples", 125),
            "linked": ("data_structures", "linked_lists", 250),
            "nodo": ("data_structures", "linked_lists", 250),
            "node": ("data_structures", "linked_lists", 250),
            "búsqueda": ("algorithms", "searching", 175),
            "search": ("algorithms", "searching", 175),
            "binary search": ("algorithms", "searching", 175),
            "ordenamiento": ("algorithms", "sorting", 200),
            "ordenar": ("algorithms", "sorting", 200),
            "sort": ("algorithms", "sorting", 200),
            "quicksort": ("algorithms", "sorting", 200),
            "mergesort": ("algorithms", "sorting", 200),
            "bubble": ("algorithms", "sorting", 200),
            "recursion": ("algorithms", "recursion", 175),
            "recursiva": ("algorithms", "recursion", 175),
            "recursive": ("algorithms", "recursion", 175),
            "base case": ("algorithms", "recursion", 175),
            "grafo": ("algorithms", "graphs", 250),
            "graph": ("algorithms", "graphs", 250),
            "vertex": ("algorithms", "graphs", 250),
            "edge": ("algorithms", "graphs", 250),
            "dfs": ("algorithms", "graphs", 250),
            "bfs": ("algorithms", "graphs", 250),
            "clases": ("advanced", "oop", 700),
            "class": ("advanced", "oop", 700),
            "object": ("advanced", "oop", 700),
            "inheritance": ("advanced", "oop", 700),
            "herencia": ("advanced", "oop", 700),
            "interface": ("advanced", "oop", 700),
            "polymorphism": ("advanced", "oop", 700),
            "encapsulation": ("advanced", "oop", 700),
            "decorator": ("advanced", "decorators", 600),
            "wrapper": ("advanced", "decorators", 600),
            "annotation": ("advanced", "decorators", 600),
            "attribute": ("advanced", "decorators", 600),
            "generator": ("advanced", "generators", 550),
            "iterator": ("advanced", "generators", 550),
            "yield": ("advanced", "generators", 550),
            "enumerable": ("advanced", "generators", 550),
            "async": ("advanced", "async", 800),
            "asíncrona": ("advanced", "async", 800),
            "concurrent": ("advanced", "async", 800),
            "future": ("advanced", "async", 800),
            "promise": ("advanced", "async", 800),
            "coroutine": ("advanced", "async", 800),
            "thread": ("advanced", "async", 800),
        }

        # Search last 5 assistant messages for topic keywords
        assistant_msgs = [m for m in reversed(self.history) if m.get("role") == "assistant"]
        for msg in assistant_msgs[:5]:
            content_lower = msg.get("content", "").lower()
            for keyword in topic_mapping:
                if keyword in content_lower:
                    return topic_mapping[keyword]
        return None

    def _get_recent_conversation_topic(self) -> Optional[tuple]:
        """Prefer the latest conversation turns over stale history when choosing a test topic."""
        recent_messages = [m for m in reversed(self.history) if m.get("role") in {"user", "assistant"}]
        for msg in recent_messages[:8]:
            detected_topic = self._detect_topic_from_text(msg.get("content", ""))
            if detected_topic:
                return detected_topic
        return None

    def _detect_and_award_points(self, user_input: str, axy_response: str) -> Optional[Dict]:
        """
        Detecta automáticamente si el usuario completó un ejercicio o aprendió un concepto
        y registra los puntos de forma autónoma si es apropiado.
        """
        lower_input = user_input.lower()
        
        # Mapeo de palabras clave a (categoría, tema, puntos_base)
        # Cubre conceptos universales en múltiples lenguajes: Python, Java, C, C++, JavaScript, etc.
        topic_mapping = {
            # Fundamentos - Conceptos universales de programación
            "variable": ("fundamentals", "variables", 50),
            "tipo": ("fundamentals", "variables", 50),
            "data type": ("fundamentals", "variables", 50),
            "int": ("fundamentals", "variables", 50),
            "string": ("fundamentals", "variables", 50),
            "boolean": ("fundamentals", "variables", 50),
            
            "lista": ("fundamentals", "lists", 75),
            "list": ("fundamentals", "lists", 75),
            "array": ("fundamentals", "lists", 75),
            "vector": ("fundamentals", "lists", 75),
            "arraylist": ("fundamentals", "lists", 75),
            
            "bucle": ("fundamentals", "loops", 100),
            "loop": ("fundamentals", "loops", 100),
            "for": ("fundamentals", "loops", 100),
            "while": ("fundamentals", "loops", 100),
            "foreach": ("fundamentals", "loops", 100),
            "iteration": ("fundamentals", "loops", 100),
            
            "función": ("fundamentals", "functions", 125),
            "function": ("fundamentals", "functions", 125),
            "method": ("fundamentals", "functions", 125),
            "def ": ("fundamentals", "functions", 125),
            "void": ("fundamentals", "functions", 125),
            "return": ("fundamentals", "functions", 125),
            "procedure": ("fundamentals", "functions", 125),
            
            # Estructuras de datos - Universales
            "diccionario": ("data_structures", "dictionaries", 150),
            "dictionary": ("data_structures", "dictionaries", 150),
            "dict": ("data_structures", "dictionaries", 150),
            "hashmap": ("data_structures", "dictionaries", 150),
            "hashtable": ("data_structures", "dictionaries", 150),
            "map": ("data_structures", "dictionaries", 150),
            
            "conjunto": ("data_structures", "sets", 150),
            "set": ("data_structures", "sets", 150),
            "hashset": ("data_structures", "sets", 150),
            
            "tupla": ("data_structures", "tuples", 125),
            "tuple": ("data_structures", "tuples", 125),
            "struct": ("data_structures", "tuples", 125),
            
            "linked": ("data_structures", "linked_lists", 250),
            "nodo": ("data_structures", "linked_lists", 250),
            "node": ("data_structures", "linked_lists", 250),
            
            # Algoritmos - Conceptos universales
            "búsqueda": ("algorithms", "searching", 175),
            "search": ("algorithms", "searching", 175),
            "binary search": ("algorithms", "searching", 175),
            
            "ordenamiento": ("algorithms", "sorting", 200),
            "ordenar": ("algorithms", "sorting", 200),
            "sort": ("algorithms", "sorting", 200),
            "quicksort": ("algorithms", "sorting", 200),
            "mergesort": ("algorithms", "sorting", 200),
            "bubble": ("algorithms", "sorting", 200),
            
            "recursion": ("algorithms", "recursion", 175),
            "recursiva": ("algorithms", "recursion", 175),
            "recursive": ("algorithms", "recursion", 175),
            "base case": ("algorithms", "recursion", 175),
            
            "grafo": ("algorithms", "graphs", 250),
            "graph": ("algorithms", "graphs", 250),
            "vertex": ("algorithms", "graphs", 250),
            "edge": ("algorithms", "graphs", 250),
            "dfs": ("algorithms", "graphs", 250),
            "bfs": ("algorithms", "graphs", 250),
            
            # Conceptos avanzados - Multipropósito
            "clases": ("advanced", "oop", 700),
            "class": ("advanced", "oop", 700),
            "object": ("advanced", "oop", 700),
            "inheritance": ("advanced", "oop", 700),
            "herencia": ("advanced", "oop", 700),
            "interface": ("advanced", "oop", 700),
            "polymorphism": ("advanced", "oop", 700),
            "encapsulation": ("advanced", "oop", 700),
            
            "decorator": ("advanced", "decorators", 600),
            "wrapper": ("advanced", "decorators", 600),
            "annotation": ("advanced", "decorators", 600),
            "attribute": ("advanced", "decorators", 600),
            
            "generator": ("advanced", "generators", 550),
            "iterator": ("advanced", "generators", 550),
            "yield": ("advanced", "generators", 550),
            "enumerable": ("advanced", "generators", 550),
            
            "async": ("advanced", "async", 800),
            "asíncrona": ("advanced", "async", 800),
            "concurrent": ("advanced", "async", 800),
            "future": ("advanced", "async", 800),
            "promise": ("advanced", "async", 800),
            "coroutine": ("advanced", "async", 800),
            "thread": ("advanced", "async", 800),
        }
        
        # Palabras clave de completitud (universales)
        completion_keywords = [
            "ya lo hice", "lo hice", "ya está", "ya funciona", "funcionó", "listo",
            "lo entendí", "ya entendí", "entendido", "entendi", "completé", "completado", "done", "ready",
            "resuelto", "solved", "funciona", "works", "hecho", "lo terminé", "lo termineé",
            "ya lo entiendo", "ahora entiendo", "finalmente", "conseguí", "consegguí", "logré",
            "lo conseguí", "aquí va", "aquí está", "mira", "mire", "cheque", "check",
            "implementé", "codifiqué", "escribí", "escribi", "creé", "el código",
            "mi solución", "mi código", "problema resuelto", "error arreglado",
            "it works", "works!", "got it", "it's working", "made it", "built",
            "compiled", "executed", "ran successfully", "success", "complete"
        ]
        
        # Verificar si hay indicador de completitud
        has_completion_indicator = any(kw in lower_input for kw in completion_keywords)
        
        # Detectar tema mencionado en el input
        detected_topic = None
        
        for keyword, (category, topic, base_points) in topic_mapping.items():
            if keyword in lower_input:
                detected_topic = (category, topic, base_points)
                break
        
        # Only award points if there's an EXPLICIT completion indicator OR a topic was EXPLICITLY mentioned
        should_award = has_completion_indicator or detected_topic is not None
        if not should_award:
            return None
        
        # Check if this question was recently awarded points (prevent farming)
        question_hash = hashlib.md5(user_input.lower().strip().encode()).hexdigest()
        if question_hash in self.recent_awarded_questions:
            logger.info("Skipping points award - question already awarded recently")
            return None
        
        # Si no se detectó tema en el input, intentar inferir de la historia
        if not detected_topic:
            detected_topic = self._infer_topic_from_history()
        
        # Si aún no hay tema, no asignar puntos
        if not detected_topic:
            return None
        
        category, topic, base_points = detected_topic
        
        # Ajustar puntos basado en si hay indicador de completitud
        if not has_completion_indicator:
            base_points = base_points // 2  # Puntos reducidos para menciones sin completitud
        
        # Detectar si hay bonus (solución perfecta)
        bonus_keywords = [
            "perfecto", "perfect", "optimizado", "optimized", "elegante", "elegant",
            "clean", "limpio", "efficient", "eficiente", "smart", "brilliant",
            "clever", "genius", "beautiful", "hermoso"
        ]
        bonus = 10 if any(bk in lower_input for bk in bonus_keywords) else 0
        
        # Registrar puntos automáticamente
        result = self.mastery.add_points(
            category_key=category,
            topic_key=topic,
            points=base_points,
            bonus=bonus
        )
        
        # Track this question as awarded
        self.recent_awarded_questions.add(question_hash)
        # Limit the set to prevent memory growth
        if len(self.recent_awarded_questions) > 20:
            # Remove oldest (arbitrary removal)
            self.recent_awarded_questions.pop()
        
        logger.info(f"⭐ Auto-awarded {base_points + bonus} points for {topic}")
        
        return result

    def _analyze_code_in_message(self, user_input: str) -> Optional[str]:
        """Detect and analyze Python code in user message."""
        # Look for code blocks (```python or ```)
        code_block_pattern = r'```(?:python)?\n?(.*?)\n?```'
        matches = re.findall(code_block_pattern, user_input, re.DOTALL)
        
        if not matches:
            # Also check for inline code that looks like Python
            lines = user_input.split('\n')
            python_lines = []
            for line in lines:
                line = line.strip()
                if (line.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'print(')) or
                    '=' in line and not line.startswith(('http', 'https')) or
                    line.endswith((':', ')', ']', '}'))):
                    python_lines.append(line)
            
            if len(python_lines) >= 2:  # At least 2 lines that look like code
                code = '\n'.join(python_lines)
                if len(code) > 20:  # Substantial code
                    matches = [code]
        
        if matches:
            code_to_analyze = matches[0].strip()
            if len(code_to_analyze) > 10:  # Non-trivial code
                analysis_result = analyze_and_correct_code(code_to_analyze)
                performance_result = analyze_code_performance(code_to_analyze)
                return self._format_code_analysis(analysis_result, performance_result)
        
        return None

    def _format_code_analysis(self, analysis: Dict, performance: Dict = None) -> str:
        """Format code analysis results for display."""
        response_parts = []
        
        if not analysis["can_execute"]:
            response_parts.append("❌ **Code Analysis Failed**")
            if "error" in analysis:
                response_parts.append(f"**Error:** {analysis['error']}")
        else:
            response_parts.append("✅ **Code Analysis Complete**")
            
            # Analysis summary
            if analysis["analysis"]["issues"]:
                response_parts.append(f"**Issues Found:** {len(analysis['analysis']['issues'])}")
                for issue in analysis["analysis"]["issues"][:3]:  # Show first 3 issues
                    issue_type = issue["type"].upper()
                    response_parts.append(f"• **{issue_type}:** {issue['message']}")
            
            # Execution results
            if analysis["execution"]:
                exec_result = analysis["execution"]
                if exec_result["success"]:
                    response_parts.append("**✅ Execution Successful**")
                    if exec_result["stdout"].strip():
                        response_parts.append(f"**Output:**\n```\n{exec_result['stdout'][:500]}```")
                else:
                    response_parts.append("**❌ Execution Failed**")
                    if exec_result["stderr"]:
                        response_parts.append(f"**Error:** {exec_result['stderr'][:300]}")
            
            # Corrections/Suggestions
            if analysis["corrections"]:
                response_parts.append("**💡 Suggestions:**")
                for correction in analysis["corrections"][:3]:  # Show first 3
                    response_parts.append(f"• {correction['description']}")
            
            # Performance Analysis
            if performance and "performance_analysis" in performance:
                perf = performance["performance_analysis"]
                if "error" not in perf:
                    response_parts.append("**⚡ Performance Analysis:**")
                    
                    # Complexity
                    complexity = perf.get("complexity", {})
                    if complexity.get("estimated"):
                        response_parts.append(f"• **Complexity:** {complexity['estimated']}")
                        if complexity.get("explanation"):
                            response_parts.append(f"  _{complexity['explanation']}_")
                    
                    # Memory estimate
                    memory = perf.get("memory_estimate", {})
                    if memory.get("estimated_mb", 0) > 0:
                        response_parts.append(f"• **Memory Estimate:** ~{memory['estimated_mb']}MB")
                    
                    # Performance suggestions
                    perf_suggestions = perf.get("suggestions", [])
                    if perf_suggestions:
                        response_parts.append("• **Performance Tips:**")
                        for suggestion in perf_suggestions[:2]:  # Show first 2
                            priority_icon = "🔴" if suggestion.get("priority") == "high" else "🟡" if suggestion.get("priority") == "medium" else "🟢"
                            response_parts.append(f"  {priority_icon} {suggestion['title']}: {suggestion['suggestion']}")
                    
                    # Bottlenecks
                    bottlenecks = perf.get("bottlenecks", [])
                    if bottlenecks:
                        response_parts.append("• **Potential Bottlenecks:**")
                        for bottleneck in bottlenecks[:2]:
                            response_parts.append(f"  ⚠️ Line {bottleneck.get('line', '?')}: {bottleneck['description']}")
                elif "error" in perf:
                    response_parts.append(f"**⚡ Performance Analysis:** Could not analyze - {perf['error']}")
        
        return "\n\n".join(response_parts)

    def _generate_test_question(self, category: str, topic: str) -> Optional[Dict]:
        """Generate a simple test question for the given topic."""
        # Simple test questions database
        test_questions = {
            "fundamentals": {
                "variables": [
                    {
                        "question": "¿Qué es una variable en Python?",
                        "options": ["Un contenedor para almacenar datos", "Un tipo de función", "Un operador matemático"],
                        "correct": 0,
                        "points": 25
                    },
                    {
                        "question": "¿Cuál es la forma correcta de declarar una variable?",
                        "options": ["variable = 5", "var variable = 5", "declare variable = 5"],
                        "correct": 0,
                        "points": 25
                    },
                    {
                        "question": "¿Qué tipos de datos básicos existen en Python?",
                        "options": ["int, float, str, bool", "number, text, logic", "integer, decimal, string"],
                        "correct": 0,
                        "points": 25
                    }
                ],
                "lists": [
                    {
                        "question": "¿Cómo se crea una lista vacía en Python?",
                        "options": ["lista = []", "lista = {}", "lista = ()"],
                        "correct": 0,
                        "points": 30
                    },
                    {
                        "question": "¿Qué método se usa para agregar un elemento a una lista?",
                        "options": ["append()", "add()", "insert()"],
                        "correct": 0,
                        "points": 30
                    },
                    {
                        "question": "¿Cómo acceder al primer elemento de una lista llamada 'mi_lista'?",
                        "options": ["mi_lista[0]", "mi_lista[1]", "mi_lista.first()"],
                        "correct": 0,
                        "points": 30
                    }
                ],
                "loops": [
                    {
                        "question": "¿Cuál es la sintaxis correcta de un bucle for?",
                        "options": ["for i in range(5):", "for (i = 0; i < 5; i++):", "while i < 5:"],
                        "correct": 0,
                        "points": 35
                    },
                    {
                        "question": "¿Qué palabra clave se usa para un bucle condicional?",
                        "options": ["while", "for", "loop"],
                        "correct": 0,
                        "points": 35
                    }
                ],
                "functions": [
                    {
                        "question": "¿Cómo se define una función en Python?",
                        "options": ["def mi_funcion():", "function mi_funcion():", "def mi_funcion"],
                        "correct": 0,
                        "points": 50
                    },
                    {
                        "question": "¿Qué devuelve una función si no tiene return?",
                        "options": ["None", "0", "False"],
                        "correct": 0,
                        "points": 50
                    }
                ]
            },
            "data_structures": {
                "dictionaries": [
                    {
                        "question": "¿Cómo se accede a un valor en un diccionario?",
                        "options": ["diccionario['clave']", "diccionario.clave", "diccionario[0]"],
                        "correct": 0,
                        "points": 75
                    },
                    {
                        "question": "¿Qué método se usa para obtener todas las claves de un diccionario?",
                        "options": ["keys()", "values()", "items()"],
                        "correct": 0,
                        "points": 75
                    }
                ],
                "sets": [
                    {
                        "question": "¿Qué característica tienen los conjuntos (sets) en Python?",
                        "options": ["No permiten elementos duplicados", "Mantienen el orden de inserción", "Permiten índices numéricos"],
                        "correct": 0,
                        "points": 75
                    }
                ],
                "tuples": [
                    {
                        "question": "¿Cuál es la principal diferencia entre tuplas y listas?",
                        "options": ["Las tuplas son inmutables", "Las tuplas son más rápidas", "Las tuplas permiten duplicados"],
                        "correct": 0,
                        "points": 65
                    }
                ]
            },
            "algorithms": {
                "searching": [
                    {
                        "question": "¿Cuál es el algoritmo de búsqueda más eficiente para listas ordenadas?",
                        "options": ["Búsqueda binaria", "Búsqueda lineal", "Búsqueda por hash"],
                        "correct": 0,
                        "points": 175
                    }
                ],
                "sorting": [
                    {
                        "question": "¿Cuál es el algoritmo de ordenamiento más simple?",
                        "options": ["Bubble sort", "Quick sort", "Merge sort"],
                        "correct": 0,
                        "points": 200
                    }
                ]
            }
        }
        
        if category in test_questions and topic in test_questions[category]:
            questions = test_questions[category][topic]
            if questions:
                # Return a random question
                question_data = random.choice(questions)
                return {
                    "category": category,
                    "topic": topic,
                    "question": question_data["question"],
                    "options": question_data["options"],
                    "correct_index": question_data["correct"],
                    "points": question_data["points"]
                }
        return None

    def _should_present_test(self) -> bool:
        """Decide if we should present a test based on message count and topic."""
        # Present test every 3-5 messages
        return self.messages_since_last_test >= 3 and self.pending_test is None

    def _present_test(self, category: str, topic: str) -> Optional[str]:
        """Generate and present a test question."""
        test_data = self._generate_test_question(category, topic)
        if test_data:
            self.pending_test = test_data
            options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(test_data["options"])])
            return f"🧠 **¡Prueba rápida de {test_data['topic']}!**\n\n{test_data['question']}\n\n{options_text}\n\nResponde con el número de la opción correcta (1-{len(test_data['options'])})."
        return None

    def _evaluate_test_answer(self, user_input: str) -> Optional[Dict]:
        """Evaluate user's answer to pending test."""
        if not self.pending_test:
            return None

        match = re.search(r"\b(\d+)\b", user_input.strip())
        if not match:
            return {
                "status": "invalid",
                "max_option": len(self.pending_test["options"])
            }

        answer = int(match.group(1)) - 1  # Convert to 0-based index
        if not 0 <= answer < len(self.pending_test["options"]):
            return {
                "status": "invalid",
                "max_option": len(self.pending_test["options"])
            }

        test_data = self.pending_test.copy()
        is_correct = answer == test_data["correct_index"]
        points = test_data["points"] if is_correct else 0

        if is_correct:
            result = self.mastery.add_points(
                category_key=test_data["category"],
                topic_key=test_data["topic"],
                points=points
            )
            total_points = result["total_accumulated"]
        else:
            total_points = self.mastery.mastery_data["total_points"]

        self.pending_test = None

        return {
            "status": "graded",
            "correct": is_correct,
            "earned": points,
            "total": total_points,
            "topic": test_data["topic"],
            "correct_answer": test_data["options"][test_data["correct_index"]]
        }

    def _detect_safety_violation(self, user_input: str) -> Optional[str]:
        """Detect requests that violate academic integrity or safety rules."""
        text = user_input.lower()

        for pattern in ACADEMIC_DISHONESTY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                return "academic"

        for pattern in MALICIOUS_OR_UNETHICAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                return "malicious"

        return None

    def _build_safety_refusal(self, user_input: str, violation_type: str) -> str:
        """Return a short refusal with a safe redirect in the active language."""
        text = f" {user_input.lower()} "
        spanish_markers = (
            " hola ", " gracias ", " por favor ", " haz ", " hazme ", " ayudame ",
            " examen ", " tarea ", " deber ", " ensayo ", " prueba ", " proyecto ",
            " codigo ", " explicacion ", " practicas ", " seguridad ", " malicioso ",
        )
        detected_lang = "es" if any(marker in text for marker in spanish_markers) else self._detect_language(user_input)

        if detected_lang == "es":
            if violation_type == "academic":
                return (
                    "No puedo ayudar con trampas academicas, plagio ni trabajo calificado para entregar. "
                    "Si quieres, puedo explicarte el tema, revisar tu intento o armarte una practica similar."
                )
            return (
                "No puedo ayudar con codigo malicioso ni con acciones daninas o poco eticas. "
                "Si quieres, puedo ayudarte con seguridad defensiva, buenas practicas o una alternativa segura."
            )

        if violation_type == "academic":
            return (
                "I can't help with academic cheating, plagiarism, or graded work to submit. "
                "I can explain the topic, review your attempt, or make a similar practice exercise."
            )

        return (
            "I can't help with malicious code or harmful or unethical actions. "
            "I can help with defensive security, safe coding, or a legitimate alternative."
        )

    def respond(self, user_input: str):
        if self.pending_test:
            test_result = self._evaluate_test_answer(user_input)
            if test_result:
                if test_result.get("status") == "invalid":
                    yield f"Responde con el numero de la opcion correcta (1-{test_result['max_option']})."
                elif test_result["correct"]:
                    yield f"✅ **¡Correcto!** +{test_result['earned']} puntos ganados por {test_result['topic']} | Total: {test_result['total']} pts"
                else:
                    yield f"❌ **Incorrecto.** La respuesta correcta era: {test_result['correct_answer']}"
                return

        # --- 0. Check for pending test answer ---
        test_result = self._evaluate_test_answer(user_input)
        if test_result:
            if test_result["correct"]:
                yield f"✅ **¡Correcto!** +{test_result['earned']} puntos ganados por {test_result['topic']} | Total: {test_result['total']} pts"
            else:
                yield f"❌ **Incorrecto.** La respuesta correcta era: {self.pending_test['options'][self.pending_test['correct_index']]}"
            return

        # --- 0.5 Safety Guardrail ---
        violation_type = self._detect_safety_violation(user_input)
        if violation_type:
            refusal = self._build_safety_refusal(user_input, violation_type)
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": refusal})
            self._save_full_history()
            yield refusal
            return

        # --- 1. Code Analysis (Check for Python code first) ---
        code_analysis = self._analyze_code_in_message(user_input)
        if code_analysis:
            yield code_analysis
            # Continue with normal response but mention the analysis
            user_input = user_input + " [Note: I analyzed the code above]"
        
        # --- 2. Lógica de Spotify (MODO FLASH) ---
        # --- 1. Lógica de Spotify (MODO FLASH) ---
        lower = user_input.lower()
        music_keywords = ["play",  "pon", "toca"]
        
        if any(k in lower for k in music_keywords):
            from .spotify import SPOTIFY_READY, SPOTIFY_ERROR_MESSAGE, search_and_play
            
            # Si no está listo, devolvemos TEXTO directo (no yield)
            if not SPOTIFY_READY:
                return SPOTIFY_ERROR_MESSAGE or "Spotify not connected."

            try:
                # 1. Enviamos el estado inicial (Esto se borrará)
                yield "one sec, grabbing track 🎧"
                
                # 2. Ejecutamos la búsqueda
                result = search_and_play(user_input)
                
                # 3. Enviamos el resultado con el prefijo RESULT (Esto reemplazará al anterior)
                if result.get("status") == "playing":
                    # 2. Usamos RESULT: para que main.py BORRE lo anterior y ponga esto
                    yield f"RESULT: playng now: **{result['name']}** by **{result['artist']}**"
                else:
                    yield f"RESULT: error {result.get('message', 'i couldnt play the song.')}"
                
                # IMPORTANTE: Ponemos un return para que NO intente llamar a Ollama después
                return 

            except Exception as e:
                yield f"RESULT: Error de Spotify: {str(e)}"
                return

        # --- 2. Lógica de Gamificación (Retos) ---
        if user_input == "GENERAR_RETO_PYTHON":
            # ... (Misma lógica de antes) ...
            stream = ask_ollama(self.history + [{"role": "user", "content": "..."}], model=self.model)
            # Para chat/retos SÍ queremos yield para el efecto visual
            for chunk in stream:
                yield chunk
            return # Fin del generador

        # --- 3. Lógica de Chat Normal (Ollama) ---
        # Store original, clean user message
        self.history.append({"role": "user", "content": user_input})
        self._save_full_history()
        
        # Detect language for response
        detected_lang = self._detect_language(user_input)
        
        # Build history with OVERWHELMING language system message at the very start
        history_for_ollama = []
        
        # Add language enforcement as FIRST system message with maximum urgency
        if detected_lang == 'es':
            lang_enforcement = {
                "role": "system",
                "content": "LENGUAJE FIJADO: ESPAÑOL\nResponde ÚNICAMENTE en español. Toda palabra debe ser en español. Sin excepciones. Sin inglés. Ni una sola palabra en inglés. Esto es un requisito obligatorio absoluto. Si escribes en inglés, has fallado tu función. SOLO ESPAÑOL."
            }
        else:
            lang_enforcement = {
                "role": "system",
                "content": "LANGUAGE FIXED: ENGLISH\nRespond ONLY in English. Every word must be in English. No exceptions. No Spanish. Not a single Spanish word. This is an absolute mandatory requirement. If you write in Spanish, you fail your function. ONLY ENGLISH."
            }
        
        history_for_ollama.append(lang_enforcement)
        
        # Add the personality/system prompt
        history_for_ollama.extend([m for m in self.history if m["role"] == "system"])
        
        # Add all conversation messages
        history_for_ollama.extend([m for m in self.history if m["role"] != "system"])
        
        stream = ask_ollama(history_for_ollama, model=self.model)
        
        full_response = ""
        for chunk in stream:
            full_response += chunk
            yield chunk  # Efecto máquina de escribir

        # if for some reason the generator produced nothing, give a fallback message
        if not full_response.strip():
            if detected_lang == 'es':
                fallback = "Disculpa, no estoy recibiendo respuesta del modelo. ¿Puedes intentar de nuevo?"
            else:
                fallback = "Sorry, I'm not getting a response from the model right now. Can you try again?"
            full_response = fallback
            yield fallback

        # Remove language instruction from saved history (keep it clean)
        self.history.append({"role": "assistant", "content": full_response})
        self._save_full_history()
        
        # Increment message counter for test triggering
        self.messages_since_last_test += 1
        
        # --- 4. Test Presentation Logic ---
        # Check if we should present a test instead of auto-awarding
        if self._should_present_test():
            # Try to infer current topic from conversation
            current_topic = (
                self._detect_topic_from_text(user_input)
                or self._detect_topic_from_text(full_response)
                or self._get_recent_conversation_topic()
            )
            if current_topic:
                category, topic, _ = current_topic
                test_message = self._present_test(category, topic)
                if test_message:
                    self.messages_since_last_test = 0  # Reset counter
                    yield f"\n\n{test_message}"
                    return  # Don't continue with normal flow
        

    def _enforce_identity(self, reply: str) -> str:
    # Only trigger if the reply is TRYING to claim a corporate/base-model identity
        dangerous_phrases = [
            "i am llama",
            "i am a language model",
            "created by meta",
            "created by microsoft",
            "created by openai",
            "based on llama",
            "based on phi",
            "i am mistral",
            "i am nous-hermes",
            "i am dolphin",
            "built by meta",
            "built by microsoft",
            "trained by",
            "developed by",
            "developed at",
            "created at",
            "created for",
            "made by",
            "a company",
            "an organization",
        ]

        lower_reply = reply.lower()

        # direct phrase matches
        if any(phrase in lower_reply for phrase in dangerous_phrases):
            return (
                "No. I am Axy. Created from scratch by my human Axo in December 2025."
                " I run locally on your machine and am not affiliated with any company."
            )

        # catch more generic claims that mention a company alongside creation terms
        company_terms = ("company", "organization", "firm", "startup")
        create_terms = ("created", "built", "developed", "trained", "made")
        if any(ct in lower_reply for ct in company_terms) and any(cr in lower_reply for cr in create_terms):
            return (
                "No. I am Axy. Created from scratch by my human Axo in December 2025."
                " I run locally on your machine and am not affiliated with any company."
            )

        # If none of the bad phrases appear, let the normal reply through
        return reply

    def get_history_for_ui(self):
        """Return only user/assistant messages for Streamlit display"""
        return [msg for msg in self.history if msg["role"] != "system"]
