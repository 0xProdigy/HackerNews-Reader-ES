from gtts import gTTS
import os
import pygame

def texto_a_voz(texto, idioma='es', archivo_salida='salida.mp3'):
    try:
        # Crear objeto gTTS
        tts = gTTS(text=texto, lang=idioma, slow=False)
        
        # Guardar archivo de audio
        tts.save(archivo_salida)
        
        # Reproducir el audio
        pygame.mixer.init()
        pygame.mixer.music.load(archivo_salida)
        pygame.mixer.music.play()
        
        # Esperar a que termine la reproducción
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
    except Exception as e:
        print(f"Error: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    texto = "Hola, esta es una prueba de texto a voz usando Python"
    texto_a_voz(texto)