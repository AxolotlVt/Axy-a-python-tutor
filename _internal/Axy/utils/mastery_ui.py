# axy/utils/mastery_ui.py
"""
Utilidades para mostrar el estado del sistema de maestría
y permitir que el usuario interactúe con él
"""

def format_progress_bar(current: int, total: int, width: int = 20) -> str:
    """Crea una barra de progreso visual"""
    filled = int((current / total) * width) if total > 0 else 0
    bar = "█" * filled + "░" * (width - filled)
    percentage = (current / total * 100) if total > 0 else 0
    return f"[{bar}] {percentage:.1f}%"


def display_mastery_summary(mastery_system) -> str:
    """Retorna un resumen visual del progreso de maestría"""
    progress = mastery_system.get_progress()
    user_level = mastery_system.get_user_level()
    next_door = mastery_system.get_next_door()
    
    summary = f"""
╔═══════════════════════════════════════════════════════════╗
║              📚 SISTEMA DE MAESTRÍA 📚                    ║
╚═══════════════════════════════════════════════════════════╝

👤 Nivel: {user_level}
⭐ Puntos totales: {progress['total_points']}/{progress['total_possible']}
   {format_progress_bar(progress['total_points'], progress['total_possible'])}

📖 Temas completados: {progress['completed_topics']}/{progress['total_topics']}
   {format_progress_bar(progress['completed_topics'], progress['total_topics'])}

🔓 Puertas desbloqueadas: {progress['unlocked_doors']}/{progress['total_doors']}
   {format_progress_bar(progress['unlocked_doors'], progress['total_doors'])}
"""
    
    if next_door:
        summary += f"""
🎯 Próxima puerta: {next_door['name']}
   Puntos necesarios: {next_door['points_needed']} más
   Progreso: {next_door['current_points']}/{next_door['required_points']}
"""
    
    return summary


def display_available_topics(mastery_system) -> str:
    """Muestra todos los temas disponibles"""
    available = mastery_system.get_available_topics()
    output = "\n🔓 TEMAS DISPONIBLES:\n"
    
    for section_key, section in available.items():
        output += f"\n📂 {section['name']} - {section['description']}\n"
        for topic_key, topic in section["topics"].items():
            difficulty = "⭐" * topic["difficulty"]
            output += f"  • {topic['title']} {difficulty}\n"
    
    return output


def display_doors_status(mastery_system) -> str:
    """Muestra el estado de todas las puertas"""
    doors = mastery_system.get_door_status()
    output = "\n🚪 ESTADO DE PUERTAS:\n"
    
    for section_key, door in doors.items():
        status_icon = "🔓" if door["unlocked"] else "🔒"
        output += f"\n{status_icon} {door['name']}\n"
        output += f"   {door['description']}\n"
        output += f"   Requisito: {door['requirement']} puntos\n"
        
        if door["unlocked"]:
            output += f"   ✓ DESBLOQUEADO\n"
        else:
            points_remaining = door['requirement'] - door['current_points']
            output += f"   Faltan: {points_remaining} puntos\n"
    
    return output


def display_recommendation(mastery_system) -> str:
    """Muestra la recomendación personal"""
    rec = mastery_system.get_recommendation()
    
    if not rec:
        return "\n🎉 ¡Felicidades! ¡Has dominado todos los temas disponibles!\n"
    
    output = f"""
💡 TE RECOMENDAMOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 {rec['title']} {rec['difficulty']}
{rec['description']}
⭐ Puntos disponibles: +{rec['points_available']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return output


def create_achievement_message(achievement: str, points: int, bonus: int = 0) -> str:
    """Crea un mensaje motivador cuando se completa algo"""
    messages = {
        "first_topic": "🎉 ¡Primer tema completado! ¡Excelente comienzo!",
        "door_unlock": "🔓 ¡NUEVA PUERTA DESBLOQUEADA! 🔓",
        "level_up": "📈 ¡SUBISTE DE NIVEL!",
        "streak": "🔥 ¡Racha activa!",
        "halfway": "🎯 ¡Ya completaste la mitad!",
    }
    
    msg = messages.get(achievement, "✨ ¡Progreso logrado!")
    total = points + bonus
    bonus_msg = f" (+ {bonus} bonus)" if bonus > 0 else ""
    
    return f"{msg}\n+{points}{bonus_msg} puntos de experiencia"
