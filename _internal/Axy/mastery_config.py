# axy/mastery_config.py
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
"""
Archivo de configuración para personalizar el Sistema de Maestría
Edita este archivo para cambiar temas, puntos, niveles, etc.
"""

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE NIVELES DEL USUARIO
# ═══════════════════════════════════════════════════════════════════════════

LEVELS = {
    "Principiante": {
        "min_points": 0,
        "max_points": 99,
        "emoji": "🌱",
        "color": "#2ecc71"  # Verde
    },
    "Aprendiz": {
        "min_points": 100,
        "max_points": 299,
        "emoji": "📚",
        "color": "#3498db"  # Azul
    },
    "Intermedio": {
        "min_points": 300,
        "max_points": 599,
        "emoji": "⚡",
        "color": "#f39c12"  # Naranja
    },
    "Avanzado": {
        "min_points": 600,
        "max_points": 999,
        "emoji": "🎯",
        "color": "#e74c3c"  # Rojo
    },
    "Maestro": {
        "min_points": 1000,
        "max_points": float('inf'),
        "emoji": "🏆",
        "color": "#9b59b6"  # Púrpura
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE SISTEMA DE PUNTOS
# ═══════════════════════════════════════════════════════════════════════════

REWARDS = {
    "exercise_completed": {
        "base": 25,
        "per_difficulty": 15,  # +15 por cada nivel de dificultad
        "description": "Completar un ejercicio"
    },
    "topic_mastered": {
        "bonus": 50,
        "description": "Dominar un tema completo"
    },
    "section_completed": {
        "bonus": 100,
        "description": "Completar una sección"
    },
    "door_unlocked": {
        "bonus": 50,
        "description": "Desbloquear una puerta"
    },
    "perfect_solution": {
        "bonus": 10,
        "description": "Solución perfecta"
    },
    "quick_solve": {
        "bonus": 5,
        "description": "Resuelto en tiempo mínimo"
    },
    "streak_bonus": {
        "base": 5,
        "per_day": 1,  # Aumenta 1 por cada día de racha
        "max": 20,
        "description": "Bonus por racha activa"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE DIFICULTADES
# ═══════════════════════════════════════════════════════════════════════════

DIFFICULTIES = {
    1: {"name": "Muy Fácil", "emoji": "⭐", "color": "#2ecc71"},
    2: {"name": "Fácil", "emoji": "⭐⭐", "color": "#3498db"},
    3: {"name": "Medio", "emoji": "⭐⭐⭐", "color": "#f39c12"},
    4: {"name": "Difícil", "emoji": "⭐⭐⭐⭐", "color": "#e74c3c"},
    5: {"name": "Muy Difícil", "emoji": "⭐⭐⭐⭐⭐", "color": "#9b59b6"},
}

# ═══════════════════════════════════════════════════════════════════════════
# MENSAJES MOTIVADORES
# ═══════════════════════════════════════════════════════════════════════════

ACHIEVEMENTS = {
    "first_topic": {
        "title": "🎉 ¡Primer tema completado!",
        "message": "Excelente comienzo. Sigue así.",
        "bonus": 10
    },
    "five_topics": {
        "title": "📖 ¡5 temas completados!",
        "message": "Vas muy rápido. Sigue aprendiendo.",
        "bonus": 25
    },
    "ten_topics": {
        "title": "🌟 ¡10 temas completados!",
        "message": "Eres un estudiante dedcado. Impresionante.",
        "bonus": 50
    },
    "door_unlocked": {
        "title": "🔓 ¡Nueva puerta desbloqueada!",
        "message": "Acceso a : {door_name}",
        "bonus": 50
    },
    "level_up": {
        "title": "📈 ¡Subiste de nivel!",
        "message": "Ahora eres {new_level}",
        "bonus": 0
    },
    "streak_7": {
        "title": "🔥 ¡Racha de 7 días!",
        "message": "Tu consistencia es admirable.",
        "bonus": 50
    },
    "perfect_week": {
        "title": "⭐ ¡Semana perfecta!",
        "message": "Completaste todos los ejercicios sin errores.",
        "bonus": 100
    },
    "halfway": {
        "title": "🎯 ¡Ya completaste la mitad!",
        "message": "Sigue así para ser un maestro.",
        "bonus": 25
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PUERTAS
# ═══════════════════════════════════════════════════════════════════════════

DOOR_COLORS = {
    "fundamentals": "#2ecc71",        # Verde
    "data_structures": "#3498db",     # Azul
    "algorithms": "#f39c12",          # Naranja
    "advanced": "#9b59b6"             # Púrpura
}

DOOR_REQUIREMENTS = {
    "fundamentals": {
        "points": 0,
        "prerequisite": None,
        "percentage_required": 0  # 0% = todas las puertas tienen acceso
    },
    "data_structures": {
        "points": 150,
        "prerequisite": "fundamentals",
        "percentage_required": 50  # Completar al menos 50% de Fundamentos
    },
    "algorithms": {
        "points": 350,
        "prerequisite": "data_structures",
        "percentage_required": 50
    },
    "advanced": {
        "points": 700,
        "prerequisite": "algorithms",
        "percentage_required": 50
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN UI
# ═══════════════════════════════════════════════════════════════════════════

UI_CONFIG = {
    "progress_bar_width": 20,
    "show_badges": True,
    "show_tips": True,
    "show_difficulty": True,
    "show_points": True,
    "animations": True,
    "dark_mode": True,
    "show_total_possible": True,
}

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE STREAK
# ═══════════════════════════════════════════════════════════════════════════

STREAK_CONFIG = {
    "enabled": True,
    "hours_reset": 24,
    "min_exercises": 1,
    "bonus_per_day": 5,
    "max_bonus": 50,
    "notification": True
}

# ═══════════════════════════════════════════════════════════════════════════
# TEMAS CUSTOMIZADOS (SI QUIERES MODIFICAR)
# ═══════════════════════════════════════════════════════════════════════════

# EJEMPLO: Agregar una nueva sección
"""
# 1. En mastery_system.py, TOPICS_TREE, agrega:

"machine_learning": {
    "name": "Machine Learning",
    "description": "Algoritmos de aprendizaje automático",
    "door_requirement": 1000,
    "prerequisite_topic": "advanced",
    "topics": {
        "decision_trees": {
            "title": "Árboles de Decisión",
            "points_cost": 1000,
            "difficulty": 5,
            "description": "Árboles para clasificación"
        },
        "neural_networks": {
            "title": "Redes Neuronales",
            "points_cost": 1200,
            "difficulty": 5,
            "description": "Deep Learning basics"
        }
    }
}

# 2. En esta configuración, agrega:

DOOR_COLORS["machine_learning"] = "#e74c3c"  # Rojo

DOOR_REQUIREMENTS["machine_learning"] = {
    "points": 1000,
    "prerequisite": "advanced",
    "percentage_required": 75
}
"""

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIÓN HELPER PARA OBTENER CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════

def get_level_emoji(points: int) -> str:
    """Obtiene el emoji del nivel según los puntos"""
    for level_name, config in LEVELS.items():
        if config["min_points"] <= points <= config["max_points"]:
            return config["emoji"]
    return LEVELS["Maestro"]["emoji"]


def get_level_name(points: int) -> str:
    """Obtiene el nombre del nivel según los puntos"""
    for level_name, config in LEVELS.items():
        if config["min_points"] <= points <= config["max_points"]:
            return level_name
    return "Maestro"


def get_points_for_reward(reward_type: str, difficulty: int = 3) -> int:
    """Calcula puntos para un reward específico"""
    if reward_type == "exercise_completed":
        return REWARDS["exercise_completed"]["base"] + \
               (REWARDS["exercise_completed"]["per_difficulty"] * difficulty)
    
    return REWARDS.get(reward_type, {}).get("bonus", 0)


def get_difficulty_info(difficulty: int) -> dict:
    """Obtiene información sobre una dificultad"""
    return DIFFICULTIES.get(difficulty, DIFFICULTIES[3])
