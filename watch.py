import os
import time
import subprocess

arquivos_monitorados = ['dados.json', 'template.html', 'build.py']

def obter_ultima_modificacao():
    return max(os.path.getmtime(f) for f in arquivos_monitorados)

def main():
    print("👀 Assistindo alterações... (dados.json, template.html)")
    print("Sempre que você der Ctrl+S, o index.html será atualizado automaticamente!")
    print("Pressione Ctrl+C para parar.\n")
    
    ultima_modificacao = obter_ultima_modificacao()
    
    try:
        while True:
            time.sleep(1)
            atual_modificacao = obter_ultima_modificacao()
            
            if atual_modificacao != ultima_modificacao:
                print("🔄 Alteração detectada! Reconstruindo index.html...")
                subprocess.run(['python3', 'build.py'])
                print("✅ index.html atualizado!\n")
                ultima_modificacao = atual_modificacao
    except KeyboardInterrupt:
        print("\nMonitoramento encerrado.")

if __name__ == '__main__':
    main()
