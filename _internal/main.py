# main.py
import os
import json
from datetime import datetime
import streamlit as st
from Axy.brain import Axy
from Axy.logging_config import setup_logging
from Axy.paths import (
    get_chat_history_path,
    get_chats_dir,
    get_users_path,
    prepare_runtime_environment,
)
from Axy.personality import get_system_prompt
from Axy.space_manager import space_manager
from Axy.streamlit_mastery import render_mastery_sidebar

# configure logging early
prepare_runtime_environment()
setup_logging()
st.set_page_config(
    page_title="Axy Your Python Mentor",
    page_icon="🦎",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS (same beautiful dark theme)
st.markdown("""
<style>
    div[data-testid="stChatMessageAvatarAssistant"] {
        background-color: #a156e0 !important;
        color: black !important;
    }
    .main { background-color: #0e0e0e; color: #e0e0e0; }
    .user-message { background: #1e1e1e; padding: 12px; border-radius: 12px; }
    .axy-message { background: #2d2d2d; padding: 12px; border-radius: 12px; border-left: 4px solid #a156e0; }
    .stTextInput > div > div > input { background-color: #1e1e1e; color: white; }
    .footer { text-align: center; margin-top: 50px; color: #666; font-size: 0.9em; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
# Render all messages from the session state

# Chat session helpers
CHATS_DIR = get_chats_dir()
CHAT_HISTORY_PATH = get_chat_history_path()
USERS_PATH = get_users_path()

def ensure_chats_dir():
    CHATS_DIR.mkdir(parents=True, exist_ok=True)

def list_chats():
    ensure_chats_dir()
    files = [path.name for path in CHATS_DIR.glob("*.json")]
    files.sort(reverse=True)
    return files

def save_current_chat(name: str):
    ensure_chats_dir()
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{safe_name}.json" if safe_name else f"{timestamp}.json"
    path = CHATS_DIR / filename
    # Save only user/assistant messagess
    messages = [m for m in st.session_state.axy.history if m.get('role') != 'system']
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    # Also save to canonical chat_history.json for compatibility
    with open(CHAT_HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

def load_chat_file(filename: str):
    path = CHATS_DIR / filename
    try:
        with open(path, 'r', encoding='utf-8') as f:
            messages = json.load(f)
    except Exception:
        messages = []
    # Build new history: system key-memory + messages
    system_msg = {"role": "system", "content": get_system_prompt()}
    st.session_state.axy.history = [system_msg] + messages
    st.session_state.messages = st.session_state.axy.get_history_for_ui()
    # persist to canonical file
    with open(CHAT_HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

def create_new_chat():
    system_msg = {"role": "system", "content": get_system_prompt()}
    st.session_state.axy.history = [system_msg]
    st.session_state.messages = st.session_state.axy.get_history_for_ui()
    # clear canonical history
    with open(CHAT_HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump([], f, indent=2, ensure_ascii=False)

# ────────────────────────────── Maestry points ──────────────────────────────
if "progress" not in st.session_state:
    st.session_state.progress = {
        "tier": 0,
        "points": 0,
        "points_needed": 5,     # checkpoints for current tier
        "last_question_id": None
    }

def update_progress(is_correct, question_id, reward=1):
    prog = st.session_state.progress

    # Avoid grinding the same question
    if prog["last_question_id"] == question_id:
        return  # no reward

    prog["last_question_id"] = question_id

    # Apply reward or penalty
    if is_correct:
        prog["points"] += reward
    else:
        prog["points"] = max(0, prog["points"] - 1)  # optional

    # Tier unlock
    if prog["points"] >= prog["points_needed"]:
        prog["tier"] += 1
        prog["points"] = 0
        prog["points_needed"] = int(prog["points_needed"] * 1.8)  # ramp difficulty


# -------------------------------- Log In ----------------------------------
def load_users():
    if USERS_PATH.exists():
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def hash_pw(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def login_flow(name_input, password_input=None):
    users = load_users()
    exact_name = name_input.strip()

    # CASE 1: Account exists
    if exact_name in users:
        if password_input is None:
            return "ask_password"  # Step 2
        if users[exact_name]["password"] == hash_pw(password_input):
            return "login_success", users[exact_name]
        else:
            return "wrong_password"

    # CASE 2: Account does NOT exist → create one
    if password_input is None:
        return "ask_new_password"

    users[exact_name] = {
        "password": hash_pw(password_input),
        "mastery_points": 0,
        "tier": 0,
        "mastery_data": {
            "total_points": 0,
            "categories": {},
            "unlocked_doors": [],
            "completed_topics": [],
            "points_per_category": {},
            "streak": 0,
            "last_activity": None
        }
    }
    save_users(users)
    return "account_created", users[exact_name]

if "login_stage" not in st.session_state:
    st.session_state.login_stage = "ask_name"

if st.session_state.login_stage == "ask_name":
    name = st.text_input("Enter your full name:")
    if name:
        result = login_flow(name)
        st.session_state.temp_name = name
        st.session_state.login_stage = result

elif st.session_state.login_stage == "ask_password":
    pw = st.text_input("Enter your password:", type="password")
    if pw:
        result = login_flow(st.session_state.temp_name, pw)
        if isinstance(result, tuple):
            result, data = result
        if result == "login_success":
            st.session_state.user = st.session_state.temp_name
            st.session_state.user_data = data  # Store full user data
            st.session_state.mastery_points = data["mastery_points"]
            st.session_state.tier = data["tier"]
            st.session_state.login_stage = "done"
            # Clear old axy instance to force it to reinitialize with new user data
            if "axy" in st.session_state:
                del st.session_state.axy
            if "messages" in st.session_state:
                del st.session_state.messages
            st.rerun()
        elif result == "wrong_password":
            st.write("Wrong password.")

elif st.session_state.login_stage == "ask_new_password":
    pw = st.text_input("Create a password:", type="password")
    if pw:
        result = login_flow(st.session_state.temp_name, pw)
        if isinstance(result, tuple):
            result, data = result
        if result == "account_created":
            st.session_state.user = st.session_state.temp_name
            st.session_state.user_data = data  # Store full user data
            st.session_state.mastery_points = data["mastery_points"]
            st.session_state.tier = data["tier"]
            st.session_state.login_stage = "done"
            st.write("Account created successfully. You are now logged in.")
            # Clear old axy instance to force it to reinitialize with new user data
            if "axy" in st.session_state:
                del st.session_state.axy
            if "messages" in st.session_state:
                del st.session_state.messages
            st.rerun()


def save_current_user_data():
    """Save the current user's data to users.json"""
    if "user" in st.session_state and "user_data" in st.session_state:
        users = load_users()
        users[st.session_state.user] = st.session_state.user_data
        save_users(users)

def sync_mastery_to_user_data():
    """Sync the mastery system's data back to st.session_state.user_data"""
    if "axy" in st.session_state and "user" in st.session_state:
        # Get current mastery data from the system
        progress = st.session_state.axy.mastery.get_progress()
        # Update user_data with latest mastery info
        if "user_data" in st.session_state:
            st.session_state.user_data["mastery_data"] = st.session_state.axy.mastery.mastery_data
            st.session_state.user_data["mastery_points"] = progress['total_points']
            st.session_state.mastery_points = progress['total_points']
            # Save it immediately
            save_current_user_data()

# ────────────────────────────── Initialize Axy & Messages ──────────────────────────────
# Determinar el user_id basado en el estado de login
user_id = st.session_state.get("user", "default")

if "axy" not in st.session_state:
    with st.spinner("Waking up Axy..."):
        # Pass user_data to MasterySystem if logged in
        user_data = st.session_state.get("user_data", {})
        st.session_state.axy = Axy(model="phi3", user_data=user_data, save_callback=save_current_user_data)
        st.session_state.messages = st.session_state.axy.get_history_for_ui()

# Only initialize messages if they don't exist (don't overwrite during reruns)
if "messages" not in st.session_state:
    st.session_state.messages = []

# ────────────────────────────── Time-Aware Greeting (only once) ──────────────────────────────
if not st.session_state.messages:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 18:
        greeting = "Good afternoon"
    elif 18 <= hour < 22:
        greeting = "Good evening"
    else:
        greeting = "Good night"

    startup_message = f"{greeting}! I'm Axy, your Python mentor. What should we learn or build today?"
    
    st.session_state.messages.append({"role": "assistant", "content": startup_message})

# Header
st.title("🦎Axy")
st.caption("Your personal Python teaching assistant · Built by Axo · 2025")

# ────────────────────────────── Sidebar: User & Mastery ──────────────────────────────
with st.sidebar:
    # Mostrar usuario loguado
    if st.session_state.login_stage == "done":
        st.header(f"👤 {st.session_state.user}")
        
        # Mostrar panel de maestría
        render_mastery_sidebar(st.session_state.axy.mastery)
        st.markdown("---")
        
        # Space Management
        space_info = space_manager.check_space_usage()
        space_warning = space_manager.get_space_warning()
        
        if space_warning:
            st.warning(space_warning)
        
        with st.expander("💾 Storage", expanded=False):
            st.metric("Data Usage", f"{space_info['total_mb']} MB", f"{space_info['usage_percent']}%")
            st.caption(f"Files: {space_info['files_count']} | Limit: {space_info['max_allowed_mb']} MB")
            
            if st.button("🧹 Clean Up Space", help="Remove old chat files and temporary data"):
                with st.spinner("Cleaning up..."):
                    cleanup_stats = space_manager.cleanup_old_data()
                    st.success("✅ Cleanup completed!")
                    st.info(f"Removed {cleanup_stats.get('files_removed', 0)} files, freed {cleanup_stats.get('space_freed_mb', 0):.1f} MB")
                    st.rerun()
        
        st.markdown("---")
    
    st.header("Chats")
    # Save current chat
    save_name = st.text_input("Save chat as", value="")
    if st.button("Save current chat"):
        save_current_chat(save_name)
        st.success("Chat saved")
        st.rerun()

    # Create new chat
    if st.button("Create new chat"):
        create_new_chat()
        st.rerun()

    st.markdown("---")
    # Load/delete existing chats
    chats = list_chats()
    if chats:
        choice = st.selectbox("Load a previous chat", options=chats)
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Load chat"):
                load_chat_file(choice)
                st.rerun()
        with col2:
            if st.button("Delete chat"):
                try:
                    os.remove(CHATS_DIR / choice)
                    st.success("Deleted")
                    st.rerun()
                except Exception:
                    st.error("Could not delete chat")
    else:
        st.info("No saved chats yet. Save one to get started.")
# ────────────────────────────── Display Chat History ──────────────────────────────
# This runs FIRST so old messages sit above the input
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    else:
        # Limit display length to prevent massive responses from overwhelming UI
        content = message["content"]
        if len(content) > 2000:
            content = content[:1997] + "..."
        st.markdown(f'<div class="axy-message"><strong>Axy:</strong> {content}</div>', unsafe_allow_html=True)

# ────────────────────────────── User Input ──────────────────────────────
if prompt := st.chat_input("Ask Axy anything about Python..."):
    points_before = st.session_state.axy.mastery.get_progress()["total_points"]

    # 1. Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user-message"><strong>You:</strong> {prompt}</div>', unsafe_allow_html=True)

    

    # 2. Obtener y mostrar respuesta de Axy (streaming)
    with st.chat_message("assistant", avatar="🦎"):
        # Contenedor mágico que permite borrar y escribir encima
        placeholder = st.empty() 
        full_response = ""
        
        # Llamamos al generador de brain.py
        response_generator = st.session_state.axy.respond(prompt)
        
        # Iteramos manualmente para detectar las "señales"
        for chunk in response_generator:
            if chunk.startswith("STATUS:"):
                # Escribe "Buscando..." (se borrará en el siguiente paso)
                placeholder.markdown(f"*{chunk.replace('STATUS:', '')}*")
            elif chunk.startswith("RESULT:"):
                # ¡BORRA lo anterior y pone el "Reproduciendo..."!
                full_response = chunk.replace("RESULT:", "")
                placeholder.markdown(full_response)
            else:
                # Comportamiento normal para el chat de Ollama (sin cursor para menos flicker)
                full_response += chunk
                placeholder.markdown(full_response)
        
        # Final render (redundant but ensures no issues)
        placeholder.markdown(full_response)

    # 3. Guardar mensaje de Axy (Usamos full_response que es la variable real)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Sync mastery data back to user data to keep everything in sync
    sync_mastery_to_user_data()
    points_after = st.session_state.axy.mastery.get_progress()["total_points"]

    if points_after != points_before:
        st.rerun()
    
    # 4. Refresh the sidebar immediately when mastery points change
    if "🎉" in full_response and ("puntos ganados" in full_response.lower() or "points earned" in full_response.lower()):
        st.rerun()

# Footer
st.markdown(f"""
<div class="footer">Axy runs 100% locally • Powered by Ollama • created by Axo</div>
""", unsafe_allow_html=True)
