import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

import requests
from bs4 import BeautifulSoup
import time
from gtts import gTTS
import pygame
import os
import tempfile

from googletrans import Translator
translator = Translator()

def traducir_texto(texto, destino='es', fuente='en'):
    if not texto or len(texto.strip()) < 3:
        return texto
    try:
        traduccion = translator.translate(texto, src=fuente, dest=destino)
        return traduccion.text
    except Exception as e:
        print(f"Error en traducción: {e}")
        return texto

def dividir_texto_por_longitud_maxima(texto, max_caracteres=4000):
    bloques = []
    texto = texto.replace('\n\n', '\n')
    while len(texto) > max_caracteres:
        corte = texto.rfind('\n', 0, max_caracteres)
        if corte == -1:
            corte = texto.rfind(' ', 0, max_caracteres)
            if corte == -1:
                corte = max_caracteres
        bloques.append(texto[:corte].strip())
        texto = texto[corte:].lstrip()
    if texto:
        bloques.append(texto.strip())
    return bloques

def get_hacker_news_headlines():
    url = "https://thehackernews.com/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        headlines_with_links = []
        story_links = soup.select('.story-link')
        for story_link in story_links:
            link = story_link.get('href', '')
            title_element = story_link.find('h2', class_='home-title')
            if title_element and link.startswith("https://thehackernews.com/"):
                title = title_element.get_text(strip=True)
                if title:
                    headlines_with_links.append({'title': title, 'link': link})
        seen_links = set()
        unique_headlines = []
        for item in headlines_with_links:
            if item['link'] not in seen_links:
                seen_links.add(item['link'])
                unique_headlines.append(item)
        return unique_headlines[:5]
    except Exception as e:
        print(f"Error obteniendo titulares: {e}")
        return []

def get_article_content(article_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(article_url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        main_title = soup.find('h1', class_='story-title')
        title_text = main_title.get_text(strip=True) if main_title else "Título no disponible"
        article_body = soup.find('div', class_='articlebody')
        if not article_body:
            return title_text, "No se pudo encontrar el contenido del artículo."
        paragraphs = article_body.find_all('p')
        content_lines = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if (text and len(text) > 10 and 
                not any(x in text.lower() for x in ['subscribe', 'function(', 'var ', 'advertisement', 'comment', 'share on', 'posted by'])):
                content_lines.append(text)
        content = "\n\n".join(content_lines)
        return title_text, content
    except Exception as e:
        return "Error al acceder al artículo", f"Detalles: {e}"

def texto_a_voz(texto, idioma='es', velocidad=False):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            temp_filename = tmp_file.name
        tts = gTTS(text=texto, lang=idioma, slow=velocidad)
        tts.save(temp_filename)
        pygame.mixer.init()
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        print("🎧 Reproduciendo audio...")

        while pygame.mixer.music.get_busy():
            time.sleep(0.5)

        pygame.mixer.music.stop()
        os.unlink(temp_filename)
    except Exception as e:
        print(f"❌ Error en texto a voz: {e}")

def mostrar_y_traducir_articulo(article_url):
    print("📖 Obteniendo artículo COMPLETO...")
    titulo_original, contenido_original = get_article_content(article_url)
    if "Error" in titulo_original:
        print(f"❌ {contenido_original}")
        return

    print("\n" + "=" * 90)
    print("📰 ARTÍCULO COMPLETO - ORIGINAL (Inglés)")
    print("=" * 90)
    print(f"🇺🇸 TÍTULO: {titulo_original}")
    print("\n" + "-" * 90)
    print("📖 CONTENIDO:")
    print(contenido_original)
    print("=" * 90)

    print("🌎 Traduciendo artículo automáticamente...")
    titulo_traducido = traducir_texto(titulo_original)
    bloques = dividir_texto_por_longitud_maxima(contenido_original)
    contenido_traducido = ""
    for i, bloque in enumerate(bloques, 1):
        print(f"   Traduciendo bloque {i}/{len(bloques)}...")
        bloque_traducido = traducir_texto(bloque)
        contenido_traducido += bloque_traducido + "\n\n"
        time.sleep(0.5)

    print("\n" + "=" * 90)
    print("📰 ARTÍCULO COMPLETO - TRADUCIDO (Español)")
    print("=" * 90)
    print(f"🇪🇸 TÍTULO: {titulo_traducido}")
    print("\n" + "-" * 90)
    print("📖 CONTENIDO TRADUCIDO:")
    print(contenido_traducido)
    print("=" * 90)

    print("\n🎧 OPCIONES DE AUDIO:")
    print("  [1] - Escuchar solo el título traducido")
    print("  [2] - Escuchar resumen traducido")
    print("  [3] - Escuchar artículo completo traducido")
    print("  [0] - Volver al menú principal")

    opcion = input("\nSelecciona una opción: ").strip()

    if opcion == '1':
        texto_a_voz(titulo_traducido)
    elif opcion == '2':
        primer_parrafo = contenido_traducido.strip().split('\n\n')[0]
        texto_a_voz(f"{titulo_traducido}. {primer_parrafo}")
    elif opcion == '3':
        texto_completo = f"{titulo_traducido}. {contenido_traducido}"
        texto_a_voz(texto_completo)
    else:
        print("↩️ Volviendo al menú principal.")

def main():
    print("=" * 90)
    print("🌎 LECTOR COMPLETO DE NOTICIAS - THE HACKER NEWS")
    print("=" * 90)

    print("Obteniendo titulares...")
    headlines = get_hacker_news_headlines()

    if not headlines:
        print("No se pudieron obtener los titulares.")
        return

    print(f"Se encontraron {len(headlines)} titulares")
    print("=" * 90)
    print("\n📰 TITULARES DISPONIBLES:\n")
    for i, item in enumerate(headlines, 1):
        print(f"{i}. {item['title']}")
        print(f"   🔗 {item['link']}\n")
    print("=" * 90)

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
                    mostrar_y_traducir_articulo(selected_item['link'])
                else:
                    print("❌ Número fuera de rango.")
            else:
                print("❌ Opción no válida.")
        except KeyboardInterrupt:
            print("\n👋 Saliendo...")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
