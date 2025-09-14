import requests
from bs4 import BeautifulSoup
import time
import re

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
        
        # Método 1: Buscar elementos con clase 'story-link' (contienen los enlaces)
        story_links = soup.select('.story-link')
        for story_link in story_links:
            link = story_link.get('href', '')
            # Buscar el título dentro de estos elementos
            title_element = story_link.find('h2', class_='home-title')
            if title_element:
                title = title_element.get_text(strip=True)
                if title and link:
                    headlines_with_links.append({'title': title, 'link': link})
        
        # Método 2: Buscar directamente los títulos y luego sus enlaces padres
        if not headlines_with_links:
            title_elements = soup.find_all('h2', class_='home-title')
            for title_element in title_elements:
                link_element = title_element.find_parent('a')
                if link_element:
                    title = title_element.get_text(strip=True)
                    link = link_element.get('href', '')
                    if title and link:
                        headlines_with_links.append({'title': title, 'link': link})
        
        # Eliminar duplicados
        unique_headlines = []
        seen_links = set()
        for item in headlines_with_links:
            if item['link'] not in seen_links:
                seen_links.add(item['link'])
                unique_headlines.append(item)
        
        return unique_headlines[:15]  # Limitar a 15 resultados
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_article_content(article_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(article_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer el título principal del artículo
        main_title = soup.find('h1', class_='story-title')
        title_text = main_title.get_text(strip=True) if main_title else "Título no disponible"
        
        # Extraer el contenido del artículo
        article_body = soup.find('div', class_='articlebody')
        
        if not article_body:
            return title_text, "No se pudo encontrar el contenido del artículo."
        
        # Extraer párrafos de texto y limpiarlos
        paragraphs = article_body.find_all('p')
        content_lines = []
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Filtrar texto no deseado (publicidad, scripts, etc.)
            if (text and len(text) > 30 and 
                not any(x in text.lower() for x in ['subscribe', 'newsletter', 'function(', 'var '])):
                content_lines.append(text)
        
        content = "\n\n".join(content_lines)
        
        return title_text, content
        
    except Exception as e:
        return f"Error al acceder al artículo", f"Detalles: {e}"

def clean_text(text):
    """Limpia el texto eliminando caracteres no deseados"""
    # Eliminar caracteres de escape y múltiples espacios
    text = re.sub(r'\s+', ' ', text)
    # Eliminar caracteres no ASCII (opcional, dependiendo de tus necesidades)
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text.strip()

def main():
    print("=" * 70)
    print("EXTRACTOR DE NOTICIAS - THE HACKER NEWS")
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
            print("  [1-15] - Leer artículo específico")
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
                    
                    # Preguntar si quiere guardar el artículo
                    save = input("\n¿Deseas guardar este artículo en un archivo? (s/n): ").strip().lower()
                    if save == 's':
                        filename = f"articulo_{choice}_{int(time.time())}.txt"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(f"Título: {title}\n")
                            f.write(f"URL: {selected_article['link']}\n")
                            f.write(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("\n" + "="*50 + "\n")
                            f.write(content)
                        print(f"Artículo guardado como: {filename}")
                    
                else:
                    print("Número fuera de rango. Por favor, elige un número de la lista.")
            else:
                print("Opción no válida. Por favor, elige un número, 'r' para recargar o 'q' para salir.")
                
        except ValueError:
            print("Por favor, ingresa un número válido.")
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()