# Aplicacao de clique automático com PyAutoGUI
import pyautogui
import time

def registrar_coordenadas(qtd_coords):
    coordenadas = []
    print("\nVocê tem 3 segundos para posicionar o mouse antes de cada coordenada ser registrada.\n")

    for i in range(qtd_coords):
        print(f"Registrando coordenada #{i + 1} em 3 segundos...")
        time.sleep(3)
        x, y = pyautogui.position()
        coordenadas.append((x, y))
        print(f"Coordenada {i + 1} registrada: ({x}, {y})")
    
    return coordenadas

def executar_rotina(coordenadas, delay, repeticoes):
    print("\nIniciando rotina de cliques...\n")
    for rep in range(repeticoes):
        print(f"Repetição {rep + 1} de {repeticoes}")
        for x, y in coordenadas:
            pyautogui.click(x, y)
            print(f"Clique em ({x}, {y})")
            time.sleep(delay)
    print("\nRotina finalizada.")

def main():
    try:
        repetir = True
        coordenadas = []
        delay = 0
        repeticoes = 0

        while repetir:
            if not coordenadas:
                delay = float(input("Quantos segundos de delay entre os cliques? "))
                repeticoes = int(input("Quantas repetições? (máximo 10) "))
                if repeticoes > 10:
                    print("O número máximo de repetições é 10. Definindo como 10.")
                    repeticoes = 10
                qtd_coords = int(input("Quantas coordenadas diferentes você quer usar? "))
                coordenadas = registrar_coordenadas(qtd_coords)

            input("\nPressione Enter para iniciar a rotina de cliques...")
            executar_rotina(coordenadas, delay, repeticoes)

            resposta = input("\nDeseja repetir com o mesmo padrão? (s/n): ").strip().lower()
            if resposta != 's':
                limpar = input("Deseja definir um novo padrão? (s/n): ").strip().lower()
                if limpar == 's':
                    coordenadas = []  # limpa tudo para refazer o padrão
                else:
                    print("Encerrando o programa. Até mais!")
                    break

    except ValueError:
        print("Por favor, insira apenas números válidos.")
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")

if __name__ == "__main__":
    main()
