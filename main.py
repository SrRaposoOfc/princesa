import yt_dlp

def baixar_melhor_resolucao(url):
    opcoes = {
        # 'bestvideo+bestaudio' garante a máxima qualidade (4K, 2K, 1080p)
        # '/best' é o fallback caso a combinação falhe
        'format': 'bestvideo+bestaudio/best',
        
        # Define o nome do arquivo final
        'outtmpl': '%(title)s.%(ext)s',
        
        # Força a mesclagem em um container estável (mp4 ou mkv)
        'merge_output_format': 'mp4',
        
        # Log para você acompanhar o progresso no console
        'noplaylist': True, 
    }

    try:
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            print("Analisando as melhores qualidades disponíveis...")
            ydl.download([url])
            print("\nDownload em alta resolução finalizado!")
    except Exception as e:
        print(f"Erro ao baixar: {e}")

# URL do vídeo (Removi os parâmetros de playlist para focar no vídeo único)
url_alvo = "https://www.youtube.com/watch?v=mrV8kK5t0V8"

baixar_melhor_resolucao(url_alvo)