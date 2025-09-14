import requests
from bs4 import BeautifulSoup
import time
import re
from gtts import gTTS
import pygame
import os
import tempfile
import urllib.parse
import json

def traducir_texto(texto, destino='es', fuente='en'):
    """
    Traduce texto usando MyMemory API con manejo de límites
    """
    try:
        if not texto or len(texto.strip()) < 3:
            return texto
            
        # Limitar longitud del texto para la API
        if len(texto) > 450:  # Reducir un poco para margen de seguridad
            texto = texto[:450]
        
        texto_codificado = urllib.parse.quote(texto)
        url = f"https://api.mymemory.translated.net/get?q={texto_codificado}&langpair={fuente}|{destino}"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data['responseData']['translatedText']
        
    except Exception as e:
        print(f"Error en traducción: {e}")
        return texto

def traducir_texto_largo(texto, destino='es', fuente='en'):
    """
    Traduce texto largo dividiéndolo en partes más pequeñas
    """
    if not texto or len(texto.strip()) < 3:
        return texto
    
    # Dividir el texto en párrafos u oraciones
    partes = re.split(r'(?<=[.!?])\s+', texto)
    partes_traducidas = []
    
    for i, parte in enumerate(partes):
        if parte.strip():  # Ignorar partes vacías
            print(f"   Traduciendo parte {i+1}/{len(partes)}...")
            traducido = traducir_texto(parte, destino, fuente)
            partes_traducidas.append(traducido)
            time.sleep(1.5)  # Pausa más larga entre requests
    
    return " ".join(partes_traducidas)

def get_hacker_news_headlines():
    url = "https://thehackernews.com/"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        headlines_with_links = []
        
        story_links = soup.select('.story-link')
        for story_link in story_links:
            link = story_link.get('href', '')
            title_element = story_link.find('h2', class_='home-title')
            if title_element:
                title = title_element.get_text(strip=True)
                if title and link:
                    headlines_with_links.append({'title': title, 'link': link})
        
        unique_headlines = []
        seen_links = set()
        for item in headlines_with_links:
            if item['link'] not in seen_links:
                seen_links.add(item['link'])
                unique_headlines.append(item)
        
        return unique_headlines[:5]
        
    except Exception as e:
        print(f"Error obteniendo titulares: {e}")
        return []

def get_article_content(article_url):
    """
    Obtiene el contenido COMPLETO de un artículo
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(article_url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer título principal
        main_title = soup.find('h1', class_='story-title')
        title_text = main_title.get_text(strip=True) if main_title else "Título no disponible"
        
        # Extraer contenido COMPLETO del artículo
        article_body = soup.find('div', class_='articlebody')
        
        if not article_body:
            return title_text, "No se pudo encontrar el contenido del artículo."
        
        # Extraer TODOS los párrafos de texto
        paragraphs = article_body.find_all('p')
        content_lines = []
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Filtrar solo texto no deseado muy obvio
            if (text and len(text) > 10 and 
                not any(x in text.lower() for x in ['subscribe to our newsletter', 'function(', 'var ', 'advertisement', 'comment', 'share on', 'posted by'])):
                content_lines.append(text)
        
        # UNIR TODO el contenido, no limitar
        content = "\n\n".join(content_lines)
        
        return title_text, content
        
    except Exception as e:
        return f"Error al acceder al artículo", f"Detalles: {e}"

def texto_a_voz(texto, idioma='es', velocidad=False):
    """Convierte texto a voz y lo reproduce"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            temp_filename = tmp_file.name
        
        tts = gTTS(text=texto, lang=idioma, slow=velocidad)
        tts.save(temp_filename)
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.stop()
        time.sleep(0.5)
        os.unlink(temp_filename)
        
    except Exception as e:
        print(f"Error en texto a voz: {e}")

def mostrar_y_traducir_articulo(article_url):
    """
    Muestra el artículo completo y opciones de traducción
    """
    print("📖 Obteniendo artículo COMPLETO...")
    titulo_original, contenido_original = get_article_content(article_url)
    
    if "Error" in titulo_original:
        print(f"❌ {contenido_original}")
        return
    
    # Mostrar contenido original primero
    print("\n" + "=" * 90)
    print("📰 ARTÍCULO COMPLETO - ORIGINAL (Inglés)")
    print("=" * 90)
    print(f"🇺🇸 TÍTULO: {titulo_original}")
    print("\n" + "-" * 90)
    print("📖 CONTENIDO:")
    print(contenido_original)
    print("=" * 90)
    
    # Preguntar si quiere traducir
    traducir = input("\n¿Deseas traducir este artículo al español? (s/n): ").strip().lower()
    
    if traducir == 's':
        print("🌎 Traduciendo título...")
        titulo_traducido = traducir_texto(titulo_original)
        
        print("📝 Traduciendo contenido (esto puede tomar varios minutos)...")
        print("   ⚠️  La traducción se hace por partes debido a límites de la API")
        
        # Dividir contenido en párrafos para traducción
        parrafos = contenido_original.split('\n\n')
        contenido_traducido = ""
        
        for i, parrafo in enumerate(parrafos, 1):
            if parrafo.strip():
                print(f"   Traduciendo párrafo {i}/{len(parrafos)}...")
                parrafo_traducido = traducir_texto(parrafo)
                contenido_traducido += parrafo_traducido + "\n\n"
                time.sleep(2)  # Pausa importante entre requests
        
        # Mostrar contenido traducido
        print("\n" + "=" * 90)
        print("📰 ARTÍCULO COMPLETO - TRADUCIDO (Español)")
        print("=" * 90)
        print(f"🇪🇸 TÍTULO: {titulo_traducido}")
        print("\n" + "-" * 90)
        print("📖 CONTENIDO TRADUCIDO:")
        print(contenido_traducido)
        print("=" * 90)
        
        # Opciones de audio para el contenido traducido
        print("\n🎧 OPCIONES DE AUDIO:")
        print("  [1] - Escuchar solo el título traducido")
        print("  [2] - Escuchar resumen traducido")
        print("  [3] - Escuchar artículo completo traducido")
        print("  [0] - Volver al menú principal")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == '1':
            print("🔊 Reproduciendo título...")
            texto_a_voz(titulo_traducido)
            
        elif opcion == '2':
            print("🔊 Reproduciendo resumen...")
            # Tomar primer párrafo como resumen
            primer_parrafo = contenido_traducido.split('\n\n')[0]
            texto_a_voz(f"{titulo_traducido}. {primer_parrafo}")
            
        elif opcion == '3':
            print("🔊 Reproduciendo artículo completo...")
            # Dividir en partes para no saturar TTS
            texto_completo = f"{titulo_traducido}. {contenido_traducido}"
            if len(texto_completo) > 1000:
                partes = [texto_completo[i:i+1000] for i in range(0, len(texto_completo), 1000)]
                for i, parte in enumerate(partes, 1):
                    print(f"Reproduciendo parte {i}/{len(partes)}...")
                    texto_a_voz(parte)
                    if i < len(partes):
                        time.sleep(1)
            else:
                texto_a_voz(texto_completo)

def main():
    pygame.mixer.init()
    
    print("=" * 90)
    print("🌎 LECTOR COMPLETO DE NOTICIAS - THE HACKER NEWS")
    print("=" * 90)
    
    # Obtener titulares
    print("Obteniendo titulares...")
    headlines = get_hacker_news_headlines()
    
    if not headlines:
        print("No se pudieron obtener los titulares.")
        return
    
    print(f"Se encontraron {len(headlines)} titulares")
    print("=" * 90)
    
    # Mostrar titulares
    print("\n📰 TITULARES DISPONIBLES:\n")
    
    for i, item in enumerate(headlines, 1):
        print(f"{i}. {item['title']}")
        print(f"   🔗 {item['link']}")
        print()
    
    print("=" * 90)
    
    # Menú interactivo
    while True:
        try:
            print("\n🎧 OPCIONES PRINCIPALES:")
            print("  [1-5] - Leer artículo COMPLETO")
            print("  [t]   - Traducir y escuchar titulares")
            print("  [q]   - Salir")
            
            choice = input("\nSelecciona una opción: ").strip().lower()
            
            if choice == 'q':
                print("¡Hasta pronto!")
                break
                
            elif choice == 't':
                print("🔊 Traduciendo y reproduciendo titulares...")
                for i, item in enumerate(headlines, 1):
                    titulo_traducido = traducir_texto(item['title'])
                    print(f"Titular {i}: {titulo_traducido}")
                    texto_a_voz(f"Titular {i}: {titulo_traducido}")
                    time.sleep(2)
                continue
                
            elif choice.isdigit():
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(headlines):
                    selected_item = headlines[choice_index]
                    
                    print(f"\n📋 ARTÍCULO SELECCIONADO:")
                    print(f"🇺🇸 {selected_item['title']}")
                    print(f"🔗 {selected_item['link']}")
                    
                    # Acceder al artículo COMPLETO
                    mostrar_y_traducir_articulo(selected_item['link'])
                    
                else:
                    print("❌ Número fuera de rango. Elige un número entre 1 y", len(headlines))
            else:
                print("❌ Opción no válida.")
                
        except ValueError:
            print("❌ Por favor, ingresa un número válido.")
        except KeyboardInterrupt:
            print("\n👋 Saliendo...")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    try:
        import pygame
        from gtts import gTTS
    except ImportError:
        print("Instalando dependencias necesarias...")
        os.system('pip install pygame gTTS beautifulsoup4 requests')
    
    main()