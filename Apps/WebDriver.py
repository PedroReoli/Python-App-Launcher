import time
import random
import undetected_chromedriver as uc

# Configuração do WebDriver
options = uc.ChromeOptions()
options.add_argument("--headless")  # Rodar sem interface gráfica (remova para visualizar)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# URL do site alvo
URL = "https://github.com/PedroReoli"

def iniciar_bot():
    driver = uc.Chrome(options=options)
    driver.get(URL)
    
    try:
        while True:
            tempo_espera = random.uniform(3, 10)  # Tempo aleatório entre refreshs
            print(f"Página carregada. Próximo refresh em {tempo_espera:.2f} segundos...")
            
            time.sleep(tempo_espera)  # Aguarda antes de atualizar
            driver.refresh()  # Atualiza a página

    except KeyboardInterrupt:
        print("Bot interrompido manualmente.")
    finally:
        driver.quit()

# Executar o bot
if __name__ == "__main__":
    iniciar_bot()
