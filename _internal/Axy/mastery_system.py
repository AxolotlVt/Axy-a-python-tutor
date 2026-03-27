# axy/mastery_system.py
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
import json
import os
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Árbol de temas con requisitos de puntos y puertas
TOPICS_TREE = {
    "fundamentals": {
        "name": "Fundamentos",
        "description": "Conceptos básicos de programación",
        "door_requirement": 0,  # Sin puerta
        "topics": {
            "variables": {
                "title": "Variables y Tipos",
                "points_cost": 0,
                "difficulty": 1,
                "description": "Almacenar datos en Python"
            },
            "lists": {
                "title": "Listas y Arrays",
                "points_cost": 50,
                "difficulty": 2,
                "description": "Colecciones ordenadas"
            },
            "loops": {
                "title": "Bucles",
                "points_cost": 75,
                "difficulty": 2,
                "description": "Repetición de código"
            },
            "functions": {
                "title": "Funciones",
                "points_cost": 100,
                "difficulty": 3,
                "description": "Reutilización de código"
            }
        }
    },
    "data_structures": {
        "name": "Estructuras de Datos",
        "description": "Organizaciones complejas de datos",
        "door_requirement": 150,  # Necesita 150 puntos totales
        "prerequisite_topic": "fundamentals",  # Y dominar Fundamentos
        "topics": {
            "dictionaries": {
                "title": "Diccionarios",
                "points_cost": 150,
                "difficulty": 3,
                "description": "Pares clave-valor"
            },
            "sets": {
                "title": "Conjuntos",
                "points_cost": 150,
                "difficulty": 3,
                "description": "Colecciones sin duplicados"
            },
            "tuples": {
                "title": "Tuplas",
                "points_cost": 125,
                "difficulty": 2,
                "description": "Colecciones inmutables"
            },
            "linked_lists": {
                "title": "Listas Enlazadas",
                "points_cost": 250,
                "difficulty": 4,
                "description": "Estructuras dinámicas"
            }
        }
    },
    "algorithms": {
        "name": "Algoritmos",
        "description": "Soluciones eficientes a problemas",
        "door_requirement": 350,
        "prerequisite_topic": "data_structures",
        "topics": {
            "searching": {
                "title": "Búsqueda",
                "points_cost": 350,
                "difficulty": 3,
                "description": "Encontrar elementos eficientemente"
            },
            "sorting": {
                "title": "Ordenamiento",
                "points_cost": 400,
                "difficulty": 4,
                "description": "Organizar datos con algoritmos"
            },
            "recursion": {
                "title": "Recursión",
                "points_cost": 300,
                "difficulty": 4,
                "description": "Funciones que se llaman a sí mismas"
            },
            "graphs": {
                "title": "Grafos",
                "points_cost": 500,
                "difficulty": 5,
                "description": "Redes y conexiones"
            }
        }
    },
    "advanced": {
        "name": "Programación Avanzada",
        "description": "Conceptos profesionales",
        "door_requirement": 700,
        "prerequisite_topic": "algorithms",
        "topics": {
            "oop": {
                "title": "Programación Orientada a Objetos",
                "points_cost": 700,
                "difficulty": 4,
                "description": "Clases e instancias"
            },
            "decorators": {
                "title": "Decoradores",
                "points_cost": 600,
                "difficulty": 5,
                "description": "Modificar funciones"
            },
            "generators": {
                "title": "Generadores",
                "points_cost": 550,
                "difficulty": 4,
                "description": "Iteración eficiente"
            },
            "async": {
                "title": "Programación Asíncrona",
                "points_cost": 800,
                "difficulty": 5,
                "description": "Código no bloqueante"
            }
        }
    }
}


class MasterySystem:
    def __init__(self, user_data: Dict = None, save_callback=None):
        self.user_data = user_data or {}
        self.save_callback = save_callback
        # Initialize mastery_data if it doesn't exist
        if "mastery_data" not in self.user_data:
            self.user_data["mastery_data"] = {
                "total_points": 0,
                "categories": {},
                "unlocked_doors": [],
                "completed_topics": [],
                "points_per_category": {},
                "streak": 0,
                "last_activity": None
            }
        self.mastery_data = self.user_data["mastery_data"]
        if "completed_topics" in self.mastery_data:
            self.mastery_data["completed_topics"] = list(dict.fromkeys(self.mastery_data["completed_topics"]))
        # Ensure mastery_points is synced
        self.user_data["mastery_points"] = self.mastery_data["total_points"]

    def _get_data_path(self) -> str:
        """Deprecated - data now stored in user_data"""
        return None

    def _load_mastery_data(self) -> Dict:
        """Deprecated - data now comes from user_data"""
        return self.mastery_data

    def _save_mastery_data(self):
        """Data is now saved through the user system"""
        # Sync mastery_points to user_data
        if "mastery_points" in self.user_data:
            self.user_data["mastery_points"] = self.mastery_data["total_points"]
        if self.save_callback:
            self.save_callback()

    def add_points(self, category_key: str, topic_key: str, points: int, 
                   bonus: int = 0) -> Dict:
        """Suma puntos por completar un tema"""
        total_earned = points + bonus
        
        # Inicializar categoría si no existe
        if category_key not in self.mastery_data["categories"]:
            self.mastery_data["categories"][category_key] = {}
        
        # Inicializar tema si no existe
        if topic_key not in self.mastery_data["categories"][category_key]:
            self.mastery_data["categories"][category_key][topic_key] = {
                "points": 0,
                "level": 1,
                "completed": False
            }
        
        # Agregar puntos
        self.mastery_data["categories"][category_key][topic_key]["points"] += total_earned
        self.mastery_data["total_points"] += total_earned
        
        # Actualizar puntos por categoría
        if category_key not in self.mastery_data["points_per_category"]:
            self.mastery_data["points_per_category"][category_key] = 0
        self.mastery_data["points_per_category"][category_key] += total_earned
        
        # Marcar como completado si acumula suficientes puntos
        topic_cost = TOPICS_TREE[category_key]["topics"][topic_key]["points_cost"]
        if self.mastery_data["categories"][category_key][topic_key]["points"] >= topic_cost:
            self.mastery_data["categories"][category_key][topic_key]["completed"] = True
            completed_topic_key = f"{category_key}/{topic_key}"
            if completed_topic_key not in self.mastery_data["completed_topics"]:
                self.mastery_data["completed_topics"].append(completed_topic_key)
            self._check_door_unlock()
        
        self._save_mastery_data()
        
        return {
            "earned": total_earned,
            "bonus": bonus,
            "total_accumulated": self.mastery_data["total_points"],
            "completed": self.mastery_data["categories"][category_key][topic_key]["completed"]
        }

    def _check_door_unlock(self):
        """Verifica si se desbloquean nuevas puertas"""
        for section_key, section in TOPICS_TREE.items():
            door_req = section["door_requirement"]
            
            # Revisar requisito de puerta
            if section_key not in self.mastery_data["unlocked_doors"]:
                if self.mastery_data["total_points"] >= door_req:
                    # Revisar requisito de tema previo si existe
                    prereq_ok = True
                    if "prerequisite_topic" in section:
                        prereq = section["prerequisite_topic"]
                        if prereq not in self.mastery_data["categories"] or \
                           not self._is_section_mastered(prereq):
                            prereq_ok = False
                    
                    if prereq_ok:
                        self.mastery_data["unlocked_doors"].append(section_key)
                        logger.info(f"🔓 Puerta desbloqueada: {section['name']}")

    def _is_section_mastered(self, section_key: str) -> bool:
        """Verifica si una sección está dominada"""
        if section_key not in self.mastery_data["categories"]:
            return False
        
        topics = self.mastery_data["categories"][section_key]
        if not topics:
            return False
        
        completed = sum(1 for t in topics.values() if t.get("completed", False))
        return completed >= max(1, len(topics) // 2)  # Al menos 50% completada

    def get_door_status(self) -> Dict:
        """Retorna el estado de todas las puertas"""
        status = {}
        for section_key, section in TOPICS_TREE.items():
            is_unlocked = section_key in self.mastery_data["unlocked_doors"]
            status[section_key] = {
                "name": section["name"],
                "unlocked": is_unlocked,
                "requirement": section["door_requirement"],
                "current_points": self.mastery_data["total_points"],
                "description": section["description"]
            }
        return status

    def get_available_topics(self) -> Dict:
        """Retorna solo los temas disponibles (puertas desbloqueadas)"""
        available = {}
        
        # Siempre disponible: Fundamentos
        if "fundamentals" in TOPICS_TREE:
            available["fundamentals"] = TOPICS_TREE["fundamentals"]
        
        # Agregar otros si las puertas están desbloqueadas
        for section_key, section in TOPICS_TREE.items():
            if section_key != "fundamentals" and section_key in self.mastery_data["unlocked_doors"]:
                available[section_key] = section
        
        return available

    def get_progress(self) -> Dict:
        """Retorna un resumen del progreso"""
        total_possible_points = sum(
            sum(t["points_cost"] for t in section["topics"].values())
            for section in TOPICS_TREE.values()
        )
        
        return {
            "total_points": self.mastery_data["total_points"],
            "total_possible": total_possible_points,
            "percentage": (self.mastery_data["total_points"] / total_possible_points * 100) if total_possible_points > 0 else 0,
            "completed_topics": len(self.mastery_data["completed_topics"]),
            "total_topics": sum(len(s["topics"]) for s in TOPICS_TREE.values()),
            "unlocked_doors": len(self.mastery_data["unlocked_doors"]),
            "total_doors": len(TOPICS_TREE)
        }

    def get_user_level(self) -> str:
        """Retorna el nivel del usuario basado en puntos"""
        points = self.mastery_data["total_points"]
        if points < 100:
            return "🌱 Principiante"
        elif points < 300:
            return "📚 Aprendiz"
        elif points < 600:
            return "⚡ Intermedio"
        elif points < 1000:
            return "🎯 Avanzado"
        else:
            return "🏆 Maestro"

    def get_next_door(self) -> Optional[Dict]:
        """Retorna la próxima puerta a desbloquear"""
        for section_key, section in sorted(TOPICS_TREE.items(), 
                                           key=lambda x: x[1]["door_requirement"]):
            if section_key not in self.mastery_data["unlocked_doors"] and section["door_requirement"] > 0:
                return {
                    "section": section_key,
                    "name": section["name"],
                    "current_points": self.mastery_data["total_points"],
                    "required_points": section["door_requirement"],
                    "points_needed": section["door_requirement"] - self.mastery_data["total_points"]
                }
        return None

    def get_recommendation(self) -> Dict:
        """Retorna un tema recomendado para estudiar"""
        # Buscar temas incompletos en secciones desbloqueadas
        available = self.get_available_topics()
        
        for section_key, section in available.items():
            for topic_key, topic in section["topics"].items():
                full_key = f"{section_key}/{topic_key}"
                
                # Si no está completado
                if full_key not in self.mastery_data["completed_topics"]:
                    return {
                        "section": section_key,
                        "topic": topic_key,
                        "title": topic["title"],
                        "difficulty": "⭐" * topic["difficulty"],
                        "description": topic["description"],
                        "points_available": topic["points_cost"]
                    }
        
        return None


# Instancia global (se puede pasar user_id diferente si es necesario)
_mastery_instance = None

def get_mastery_system(user_data: Dict = None, save_callback=None) -> MasterySystem:
    """Retorna la instancia del sistema de maestría"""
    global _mastery_instance
    if _mastery_instance is None or _mastery_instance.user_data != user_data:
        _mastery_instance = MasterySystem(user_data=user_data, save_callback=save_callback)
    return _mastery_instance
