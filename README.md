# Python App Launcher

Um lançador de aplicativos profissional e minimalista desenvolvido em Python com interface PyQt5.

## 🚀 Características

- **Interface Profissional**: Design moderno e responsivo usando PyQt5
- **Detecção Automática**: Escaneia automaticamente aplicativos em diferentes linguagens
- **Inferência Inteligente**: Detecta automaticamente a linguagem de programação
- **Organização por Tags**: Sistema de tags para categorizar aplicativos
- **Pesquisa e Filtros**: Busca rápida e filtros por linguagem e tags
- **Execução Segura**: Executa aplicativos sem alterar o diretório de trabalho
- **Configurações Flexíveis**: Sistema completo de configurações personalizáveis

## 📋 Pré-requisitos

- Python 3.7 ou superior
- PyQt5

## 🛠️ Instalação

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd Python-App-Launcher
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação:**
```bash
python main.py
```

## 📁 Estrutura do Projeto

```
Python-App-Launcher/
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências do projeto
├── README.md              # Documentação
├── gui/                   # Módulo de interface gráfica
│   ├── __init__.py
│   └── main_window.py     # Janela principal
├── core/                  # Lógica principal
│   ├── __init__.py
│   └── app_manager.py     # Gerenciador de aplicativos
├── config/                # Configurações
│   ├── __init__.py
│   └── settings_manager.py # Gerenciador de configurações
├── apps/                  # Diretório de aplicativos (criado automaticamente)
├── data/                  # Dados persistentes (criado automaticamente)
├── config/                # Arquivos de configuração (criado automaticamente)
└── assets/                # Recursos (ícones, imagens)
```

## 🎯 Como Usar

### 1. Adicionando Aplicativos

Coloque seus aplicativos na pasta `apps/` (criada automaticamente). O sistema suporta:

- **Scripts Python** (.py)
- **Aplicativos JavaScript** (.js)
- **Aplicativos Java** (.java, .jar)
- **Executáveis Windows** (.exe)
- **Scripts Shell** (.sh)
- **Scripts Batch** (.bat)
- **Scripts PowerShell** (.ps1)
- **E muito mais...**

### 2. Organização

Os aplicativos podem ser organizados em subpastas:
```
apps/
├── Python/
│   ├── meu_app.py
│   └── outro_app.py
├── JavaScript/
│   └── web_app.js
├── Java/
│   └── aplicativo.jar
└── Executaveis/
    └── programa.exe
```

### 3. Interface

- **Lista de Aplicativos**: Exibe todos os aplicativos detectados
- **Barra de Pesquisa**: Busca rápida por nome
- **Filtros**: Filtre por linguagem ou tags
- **Painel de Detalhes**: Informações completas do aplicativo selecionado
- **Botões de Ação**: Execute aplicativos com um clique

## 🔧 Configurações

As configurações são salvas em `config/settings.json` e incluem:

- Diretório de aplicativos
- Tema da interface
- Tamanho e posição da janela
- Configurações de execução
- Preferências de interface

## 🎨 Temas

A aplicação suporta temas claro e escuro (configurável nas configurações).

## 📊 Dados Persistentes

Os dados dos aplicativos são salvos em `data/app_data.json` e incluem:

- Nome e caminho do aplicativo
- Linguagem inferida
- Comando de execução
- Tags personalizadas

## 🚀 Execução de Aplicativos

O sistema executa aplicativos de forma segura:

- **Não altera o diretório de trabalho**
- **Usa comandos apropriados para cada linguagem**
- **Suporte multiplataforma** (Windows, Linux, macOS)
- **Execução não-bloqueante**

## 🔍 Detecção de Linguagens

O sistema detecta automaticamente a linguagem baseada em:

1. **Extensão do arquivo** (.py → Python, .js → JavaScript, etc.)
2. **Conteúdo do arquivo** (shebang, palavras-chave)
3. **Permissões de execução** (sistemas Unix)

## 🏷️ Sistema de Tags

Adicione tags personalizadas aos seus aplicativos para melhor organização:

- **Produtividade**
- **Desenvolvimento**
- **Jogos**
- **Ferramentas**
- **E muito mais...**

## 🛡️ Segurança

- Execução segura de aplicativos
- Validação de arquivos
- Tratamento de erros robusto
- Logs de execução

## 🔧 Desenvolvimento

### Estrutura de Módulos

- **`main.py`**: Inicialização da aplicação PyQt
- **`gui/main_window.py`**: Interface gráfica principal
- **`core/app_manager.py`**: Lógica de detecção e execução
- **`config/settings_manager.py`**: Gerenciamento de configurações

### Adicionando Novas Linguagens

Para adicionar suporte a uma nova linguagem, edite `core/app_manager.py`:

1. Adicione a extensão ao `language_map`
2. Adicione o comando de execução ao `execution_commands`

### Personalizando a Interface

A interface pode ser personalizada editando `gui/main_window.py`:

- Cores e temas
- Layout e componentes
- Comportamento dos widgets

## 📝 Logs

A aplicação gera logs para debugging:

- Detecção de aplicativos
- Execução de comandos
- Erros e exceções

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🆘 Suporte

Para suporte e dúvidas:

- Abra uma issue no GitHub
- Consulte a documentação
- Verifique os logs de erro

## 🔄 Atualizações

O sistema verifica automaticamente por atualizações e pode ser configurado para atualização automática.

---

**Desenvolvido com ❤️ em Python e PyQt5** 