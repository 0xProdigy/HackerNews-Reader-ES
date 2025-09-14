import requests
from bs4 import BeautifulSoup
import time
import re
from gtts import gTTS
import pygame
import os
import tempfile

def get_hacker_news_headlines():
    url = "https://thehackernews.com/"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer titulares y enlaces
        headlines_with_links = []
        
        # Buscar elementos con clase 'story-link'
        story_links = soup.select('.story-link')
        for story_link in story_links:
            link = story_link.get('href', '')
            title_element = story_link.find('h2', class_='home-title')
            if title_element:
                title = title_element.get_text(strip=True)
                if title and link:
                    headlines_with_links.append({'title': title, 'link': link})
        
        # Eliminar duplicados
        unique_headlines = []
        seen_links = set()
        for item in headlines_with_links:
            if item['link'] not in seen_links:
                seen_links.add(item['link'])
                unique_headlines.append(item)
        
        return unique_headlines[:10]
        
    except Exception as e:
        print(f"Error obteniendo titulares: {e}")
        return []

def get_article_content(article_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(article_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer título principal
        main_title = soup.find('h1', class_='story-title')
        title_text = main_title.get_text(strip=True) if main_title else "Título no disponible"
        
        # Extraer contenido del artículo
        article_body = soup.find('div', class_='articlebody')
        
        if not article_body:
            return title_text, "No se pudo encontrar el contenido del artículo."
        
        # Extraer párrafos de texto
        paragraphs = article_body.find_all('p')
        content_lines = []
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            if (text and len(text) > 30 and 
                not any(x in text.lower() for x in ['subscribe', 'newsletter', 'function(', 'var '])):
                content_lines.append(text)
        
        content = "\n\n".join(content_lines)
        
        return title_text, content
        
    except Exception as e:
        return f"Error al acceder al artículo", f"Detalles: {e}"

def texto_a_voz(texto, idioma='es', velocidad=False):
    """Convierte texto a voz y lo reproduce"""
    try:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            temp_filename = tmp_file.name
        
        # Crear objeto gTTS
        tts = gTTS(text=texto, lang=idioma, slow=velocidad)
        
        # Guardar archivo de audio temporal
        tts.save(temp_filename)
        
        # Inicializar pygame mixer si no está inicializado
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Cargar y reproducir audio
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        
        # Esperar a que termine la reproducción
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        # Cerrar y eliminar archivo temporal
        pygame.mixer.music.stop()
        time.sleep(0.5)  # Pequeña pausa
        os.unlink(temp_filename)
        
    except Exception as e:
        print(f"Error en texto a voz: {e}")
        # Limpiar archivo temporal en caso de error
        try:
            os.unlink(temp_filename)
        except:
            pass

def limpiar_texto_para_voz(texto):
    """Limpia el texto para que suene mejor en TTS"""
    # Reemplazar caracteres problemáticos
    reemplazos = {
        '&': 'y',
        '#': 'número ',
        '@': 'arroba ',
        '%': 'por ciento ',
        '|': ', ',
        '//': ', ',
        '`': '',
        '~': '',
        '...': '. ',
        '..': '. '
    }
    
    for char, reemplazo in reemplazos.items():
        texto = texto.replace(char, reemplazo)
    
    # Limitar longitud para no saturar TTS
    if len(texto) > 1000:
        texto = texto[:1000] + "... Continúa leyendo en pantalla."
    
    return texto

def main():
    # Inicializar pygame mixer
    pygame.mixer.init()
    
    print("=" * 70)
    print("EXTRACTOR DE NOTICIAS CON LECTOR DE VOZ - THE HACKER NEWS")
    print("=" * 70)
    
    # Obtener titulares
    headlines = get_hacker_news_headlines()
    
    if not headlines:
        print("No se pudieron obtener los titulares. Verifica tu conexión a internet.")
        return
    
    # Mostrar titulares numerados
    print("\n📰 ÚLTIMOS TITULARES:\n")
    for i, item in enumerate(headlines, 1):
        print(f"{i:2d}. {item['title']}")
    
    print("\n" + "=" * 70)
    
    # Menú interactivo
    while True:
        try:
            print("\nOpciones:")
            print("  [1-10] - Leer artículo específico")
            print("  [t]    - Escuchar todos los titulares")
            print("  [r]    - Recargar titulares")
            print("  [q]    - Salir")
            
            choice = input("\nSelecciona una opción: ").strip().lower()
            
            if choice == 'q':
                print("¡Hasta pronto!")
                break
                
            elif choice == 'r':
                print("Recargando titulares...")
                headlines = get_hacker_news_headlines()
                if headlines:
                    print("\n📰 TITULARES ACTUALIZADOS:\n")
                    for i, item in enumerate(headlines, 1):
                        print(f"{i:2d}. {item['title']}")
                else:
                    print("Error al recargar titulares.")
                continue
                
            elif choice == 't':
                print("Leyendo todos los titulares...")
                for i, item in enumerate(headlines, 1):
                    texto_limpiado = limpiar_texto_para_voz(f"Título {i}: {item['title']}")
                    texto_a_voz(texto_limpiado)
                    time.sleep(1)  # Pausa entre titulares
                continue
                
            elif choice.isdigit():
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(headlines):
                    selected_article = headlines[choice_index]
                    print(f"\n📖 Cargando: {selected_article['title']}")
                    print("=" * 70)
                    
                    # Obtener contenido del artículo
                    title, content = get_article_content(selected_article['link'])
                    
                    # Mostrar contenido
                    print(f"\n{title}")
                    print("-" * 50)
                    print(content)
                    print("=" * 70)
                    
                    # Opciones de audio
                    print("\nOpciones de audio:")
                    print("  [1] - Escuchar título solamente")
                    print("  [2] - Escuchar contenido completo")
                    print("  [3] - Escuchar resumen (primeros párrafos)")
                    print("  [0] - Volver al menú principal")
                    
                    audio_choice = input("\nSelecciona opción de audio: ").strip()
                    
                    if audio_choice == '1':
                        texto_limpiado = limpiar_texto_para_voz(f"Título: {title}")
                        texto_a_voz(texto_limpiado)
                        
                    elif audio_choice == '2':
                        texto_completo = limpiar_texto_para_voz(f"{title}. {content}")
                        texto_a_voz(texto_completo)
                        
                    elif audio_choice == '3':
                        # Primeros 3 párrafos como resumen
                        parrafos = content.split('\n\n')
                        resumen = ' '.join(parrafos[:3])
                        texto_resumen = limpiar_texto_para_voz(f"Resumen: {title}. {resumen}")
                        texto_a_voz(texto_resumen)
                    
                else:
                    print("Número fuera de rango. Por favor, elige un número de la lista.")
            else:
                print("Opción no válida.")
                
        except ValueError:
            print("Por favor, ingresa un número válido.")
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == "__main__":
    # Instalar dependencias si no están instaladas
    try:
        import pygame
    except ImportError:
        print("Instalando dependencias necesarias...")
        os.system('pip install pygame gTTS')
    
    main()