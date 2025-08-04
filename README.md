# Auto Clicker - Automatizador de Cliques

Um aplicativo Python com interface gráfica para automatizar cliques na tela, permitindo criar sequências de cliques personalizadas para rotinas automatizadas.

## 🚀 Funcionalidades

- **Captura de Coordenadas**: Capture posições do mouse para criar sequências de cliques
- **Configuração de Delays**: Defina intervalos entre cliques e repetições
- **Repetições**: Execute a mesma sequência múltiplas vezes
- **Sequências Salvas**: Salve e carregue sequências personalizadas
- **Hotkeys**: Use teclas de atalho para controle rápido
- **Interface Intuitiva**: Interface gráfica moderna e fácil de usar

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Windows 10/11 (testado)

## 🛠️ Instalação

1. **Clone ou baixe o projeto**
2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Como Usar

### 1. Executar o Aplicativo
```bash
python app_launcher.py
```

### 2. Configurar Parâmetros
- **Delay entre cliques**: Tempo em segundos entre cada clique
- **Número de repetições**: Quantas vezes executar a sequência completa
- **Delay entre repetições**: Tempo de espera entre cada repetição

### 3. Capturar Coordenadas
1. Clique em **"Capturar Coordenadas (F6)"**
2. Posicione o mouse onde deseja clicar
3. Pressione **F6** para capturar a posição
4. Repita para adicionar mais pontos à sequência

### 4. Executar Automação
1. Configure os parâmetros desejados
2. Clique em **"Iniciar Automação (F7)"**
3. Para parar, pressione **Ctrl+Alt+S**

### 5. Salvar/Carregar Sequências
- **Salvar**: Capture coordenadas e clique em "Salvar Sequência"
- **Carregar**: Selecione uma sequência salva e clique em "Carregar Sequência"
- **Deletar**: Selecione e clique em "Deletar Sequência"

## ⌨️ Hotkeys

| Tecla | Função |
|-------|--------|
| F6 | Capturar coordenada atual |
| F7 | Iniciar automação |
| Ctrl+Alt+S | Parar automação |

## 📁 Estrutura do Projeto

```
Python-App-Launcher/
├── app_launcher.py          # Aplicativo principal
├── requirements.txt         # Dependências
├── README.md              # Documentação
├── saved_sequences.json   # Sequências salvas (criado automaticamente)
└── markdown/              # Documentação técnica
    ├── checklist.md
    ├── atualizacoes.md
    └── chat-context.md
```

## 🔧 Configurações Avançadas

### PyAutoGUI
- **FAILSAFE**: Mova o mouse para o canto superior esquerdo para parar
- **PAUSE**: Pausa padrão entre ações (0.1 segundos)

### Threading
- A automação roda em thread separada para não travar a interface
- Interface permanece responsiva durante execução

## 📊 Formato dos Dados

### Sequências Salvas (JSON)
```json
{
  "nome_da_sequencia": {
    "name": "nome_da_sequencia",
    "coordinates": [
      {
        "index": 1,
        "x": 100,
        "y": 200,
        "delay": 1.0
      }
    ],
    "delay": "1.0",
    "repetitions": "1",
    "repetition_delay": "2.0",
    "created": "2024-01-01T12:00:00"
  }
}
```

## ⚠️ Avisos Importantes

1. **Use com Responsabilidade**: Automatize apenas tarefas que você tem permissão para automatizar
2. **Teste Primeiro**: Sempre teste em ambiente seguro antes de usar em produção
3. **Backup**: Mantenha backup das suas sequências salvas
4. **Segurança**: O aplicativo pode ser interrompido movendo o mouse para o canto superior esquerdo

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError"
- Instale as dependências: `pip install -r requirements.txt`

### Erro: "Permission denied"
- Execute como administrador se necessário

### Aplicativo não responde
- Pressione Ctrl+Alt+S para parar
- Mova o mouse para o canto superior esquerdo

### Hotkeys não funcionam
- Verifique se não há conflitos com outros aplicativos
- Reinicie o aplicativo

## 🔄 Versões

- **v1.0.0**: Versão inicial com funcionalidades básicas
  - Captura de coordenadas
  - Automação de cliques
  - Salvamento de sequências
  - Interface gráfica completa

## 📝 Licença

Este projeto é de uso livre para fins educacionais e pessoais.

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas! Entre em contato para contribuir.

---

**Desenvolvido com ❤️ para automatização de tarefas repetitivas** 