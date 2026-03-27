# axy/streamlit_mastery.py
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
Componentes de Streamlit para el Sistema de Maestría
Colócalo en main.py para mostrar la barra de progreso interactiva
"""

try:
    import streamlit as st
except ImportError:
    st = None


def render_mastery_sidebar(mastery_system):
    """
    Renderiza el sistema de maestría en el sidebar de Streamlit
    
    Uso en main.py:
    ```python
    from Axy.streamlit_mastery import render_mastery_sidebar
    
    with st.sidebar:
        render_mastery_sidebar(axy.mastery)
    ```
    """
    if st is None:
        return
    
    with st.sidebar:
        st.markdown("---")
        
        # Encabezado
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 📚 Maestría")
        with col2:
            user_level = mastery_system.get_user_level()
            st.markdown(f"### {user_level}")
        
        # Progreso general
        progress = mastery_system.get_progress()
        
        with st.expander("⭐ Puntos", expanded=True):
            st.metric(
                "Puntos Totales",
                f"{progress['total_points']}/{progress['total_possible']}",
                f"{progress['percentage']:.1f}%"
            )
            if progress['total_possible'] > 0:
                ratio = min(progress['total_points'] / progress['total_possible'], 1.0)
                st.progress(ratio)
            else:
                st.progress(0.0)
        
        with st.expander("📖 Temas Completados"):
            cols = st.columns(2)
            with cols[0]:
                st.metric("Completados", progress['completed_topics'])
            with cols[1]:
                st.metric("Totales", progress['total_topics'])
            if progress['total_topics'] > 0:
                st.progress(progress['completed_topics'] / progress['total_topics'])
            else:
                st.progress(0)
        
        with st.expander("🔓 Puertas Desbloqueadas"):
            cols = st.columns(2)
            with cols[0]:
                st.metric("Desbloqueadas", progress['unlocked_doors'])
            with cols[1]:
                st.metric("Totales", progress['total_doors'])
            if progress['total_doors'] > 0:
                st.progress(progress['unlocked_doors'] / progress['total_doors'])
            else:
                st.progress(0)
        
        # Próxima puerta
        next_door = mastery_system.get_next_door()
        if next_door and next_door['required_points'] > 0:
            st.warning(f"🎯 Próxima puerta: **{next_door['name']}**")
            if next_door['points_needed'] > 0:
                st.caption(f"Faltan {next_door['points_needed']} puntos")
            else:
                st.caption(f"¡Excedido por {-next_door['points_needed']} puntos!")
            progress_pct = next_door['current_points'] / next_door['required_points'] if next_door['required_points'] > 0 else 0
            st.progress(min(progress_pct, 1.0))
        
        st.markdown("---")


def render_mastery_main(mastery_system):
    """
    Renderiza una vista detallada en la zona principal
    
    Uso en main.py:
    ```python
    from Axy.streamlit_mastery import render_mastery_main
    
    if st.button("Ver Maestría"):
        render_mastery_main(axy.mastery)
    ```
    """
    if st is None:
        return
    
    # Resumen
    progress = mastery_system.get_progress()
    user_level = mastery_system.get_user_level()
    
    st.markdown(f"# {user_level} Sistema de Maestría")
    
    # Métrica general
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Puntos Totales", f"{progress['total_points']}/{progress['total_possible']}")
    with col2:
        st.metric("Temas Completados", f"{progress['completed_topics']}/{progress['total_topics']}")
    with col3:
        st.metric("Progreso Global", f"{progress['percentage']:.1f}%")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📚 Temas Disponibles", "🔓 Estado de Puertas", "💡 Recomendación", "📊 Detalles"]
    )
    
    # Tab 1: Temas disponibles
    with tab1:
        available = mastery_system.get_available_topics()
        
        for section_key, section in available.items():
            st.subheader(section["name"])
            st.caption(section["description"])
            
            cols = st.columns(2)
            for idx, (topic_key, topic) in enumerate(section["topics"].items()):
                with cols[idx % 2]:
                    difficulty = "⭐" * topic["difficulty"]
                    with st.container(border=True):
                        st.markdown(f"**{topic['title']}** {difficulty}")
                        st.caption(topic["description"])
                        st.caption(f"🎯 +{topic['points_cost']} puntos")
    
    # Tab 2: Estado de puertas
    with tab2:
        doors = mastery_system.get_door_status()
        
        for section_key, door in doors.items():
            col1, col2 = st.columns([2, 3])
            
            with col1:
                status = "✅ Desbloqueada" if door["unlocked"] else "🔒 Bloqueada"
                st.markdown(f"### {door['name']}\n{status}")
            
            with col2:
                st.caption(door["description"])
                if door["unlocked"]:
                    st.success("✓ Acceso disponible")
                else:
                    points_needed = door['requirement'] - door['current_points']
                    st.info(f"Requisito: {door['requirement']} puntos")
                    st.caption(f"Faltan: {points_needed} puntos")
                    if door['requirement'] > 0:
                        progress_pct = door['current_points'] / door['requirement']
                        st.progress(progress_pct)
                    else:
                        st.progress(0)
    
    # Tab 3: Recomendación
    with tab3:
        rec = mastery_system.get_recommendation()
        
        if not rec:
            st.success("🎉 ¡Has dominado todos los temas disponibles!")
        else:
            difficulty = "⭐" * rec['difficulty']
            with st.container(border=True):
                st.markdown(f"## 💡 {rec['title']} {difficulty}")
                st.markdown(f"> {rec['description']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"**+{rec['points_available']}** puntos")
                with col2:
                    st.caption(f"Sección: {rec['section']}")
                
                if st.button("Comenzar este tema"):
                    st.info(f"Perfecto, vamos a aprender {rec['title']}")
    
    # Tab 4: Detalles completos
    with tab4:
        st.subheader("📊 Estadísticas Detalladas")
        
        # Puntos por categoría
        if mastery_system.mastery_data["points_per_category"]:
            st.bar_chart(mastery_system.mastery_data["points_per_category"])
        
        # Temas completados
        completed = mastery_system.mastery_data["completed_topics"]
        if completed:
            st.subheader("✅ Temas Completados")
            for topic in completed:
                st.caption(f"• {topic.replace('/', ' > ')}")
        
        # JSON raw
        with st.expander("👨‍💻 Ver datos JSON"):
            st.json(mastery_system.mastery_data)


def render_achievement_popup(title: str, points: int, bonus: int = 0):
    """
    Muestra un popup de logro con animación
    
    Uso:
    ```python
    render_achievement_popup("Tema Completado", 50, bonus=10)
    ```
    """
    if st is None:
        return
    
    with st.toast(f"🎉 {title}", icon="🎉"):
        st.markdown(f"### ✨ +{points + bonus} puntos")
        if bonus > 0:
            st.markdown(f"Bonus: +{bonus} 🎁")
