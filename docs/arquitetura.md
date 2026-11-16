# Arquitetura de Software

Este documento descreve as decisões arquiteturais e a divisão de módulos do **Docentia** (Assistente de Revisão de TCC). A arquitetura foi pensada de maneira modular, separando a interface gráfica da lógica de persistência e do motor de validação de citações.

## Visão Geral do Sistema

O sistema segue o padrão conceitual **Model-View-Controller (MVC)** de forma adaptada para aplicações desktop:
- **Model**: Módulo `database.py` (Gerencia banco de dados, configurações persistentes e objetos de negócio).
- **View/Controller**: Módulo `main.py` (Lida com o layout PyQt6 e reage às ações do usuário em tela).
- **Tema e Assets**: Módulo `ui_theme.py` (Define as folhas de estilo `DARK_GLASS_QSS` e `LIGHT_PAPER_QSS`, tokens visuais e utilitários para ícones/ilustrações SVG em `assets/`).
- **Core Engine (Serviço)**: Módulo `validador_citacoes.py` (Lógica de processamento de texto e expressões regulares).

## Pilha Tecnológica (Tech Stack)

1. **Python 3.x**: Linguagem base escolhida pela vasta disponibilidade de bibliotecas de processamento de texto e dados.
2. **PyQt6**: Framework escolhido para a UI por oferecer suporte robusto a controles customizados (QSS), multithreading e visualização de canvas de PDF (`QGraphicsScene`).
3. **PyMuPDF (`fitz`)**: Motor de PDF ultra-rápido para leitura do documento em tela e extração de coordenadas de texto.
4. **SQLite3 (`database.py`)**: Banco de dados relacional embarcado, garantindo que o app possa ser usado offline sem instalações pesadas.
5. **python-docx / QPdfWriter**: Bibliotecas responsáveis pela geração e exportação de relatórios locais (.docx e .pdf).
6. **Pandas / Openpyxl**: Exportação e modelagem das planilhas de relatórios de validação de citação em `.xlsx`.

## Descrição dos Módulos

### 1. `main.py` (Interface Gráfica e Lógica de Fluxo)
Este é o ponto de entrada da aplicação (`entry point`). Responsável por instanciar a `QApplication`.
- **`TCCAssistantApp` (QMainWindow)**: Classe principal que gerencia o estado da navegação. Controla o que é exibido no painel central (Dashboard de Projetos vs. Workspace de Revisão).
- **`PDFViewer` (QGraphicsView)**: Um componente customizado herdado do Qt. Ele gerencia o carregamento de páginas do PyMuPDF, rasteriza-as como `QPixmap` e desenha na tela. Implementa também a seleção com "Rubber Band" e a extração de texto via caixa delimitadora (`get_textbox()`).
- **Exportação e E-mail**: Utiliza bibliotecas internas como `smtplib` em junção com o parser DOCX/QTextDocument para formatar os anexos e submeter vias de e-mail ao orientador configurado no projeto.

### 2. `database.py` (Persistência)
Camada isolada para lidar com requisições SQL, resolvendo `tcc_assistant.db` sempre no diretório da aplicação (`BASE_DIR`). Garante que os formulários e listas da UI possam carregar dados limpos em formato de dicionários (`sqlite3.Row`).
- Gerencia três tabelas: **Projetos** (`projects` — metadados do aluno, orientador, caminhos), **Anotações** (`annotations` — vínculo 1:N com Projeto, armazenando recortes, páginas e anotações do revisor) e **Configurações** (`app_settings` — chave/valor para persistência do tema ativo via `get_setting()` / `set_setting()`).
- Possui uma lógica simples de **migrations** no `init_db()` usando `PRAGMA table_info` para criar dinamicamente novas colunas (como `advisor_name` e `advisor_email` caso não existam).

### 3. `ui_theme.py` (Temas e Recursos Visuais)
Centraliza a identidade visual do **Docentia** e o carregamento de recursos relativos à pasta raiz (`BASE_DIR`):
- **`DARK_GLASS_QSS` e `LIGHT_PAPER_QSS`**: Folhas de estilo QSS completas para os modos Escuro e Claro.
- **`THEME_TOKENS`**: Dicionário com cores adaptativas para o canvas do PDF (`scene_bg`), ícones e abas de categoria.
- **`load_svg_icon()` / `load_svg_pixmap()` / `resource_path()`**: Renderizam ícones e ilustrações SVG de `assets/` com suporte a HiDPI e colorização dinâmica.

### 4. `validador_citacoes.py` (Motor de Expressões Regulares)
Este arquivo é puramente focado em extração de NLP/Regex. Ele processa PDFs inteiros de maneira invisível ao usuário.
- **Extração da Bibliografia**: Navega nas páginas do documento de trás para frente até identificar a seção "REFERÊNCIAS". Isola o conteúdo e corta com segurança ao encontrar blocos delimitadores como "ANEXO" ou "APÊNDICE".
- **Busca por Padrões**: Utiliza RegEx compiladas (`pattern1`, `pattern2`) para capturar chamadas no texto como `Autor (Ano)` ou `(AUTOR, Ano)`.
- **Heurística de Ignorar Falsos Positivos**: Ignora citações vindas de imagens e tabelas (ex: "Fonte: Autor (2023)") graças a regras explícitas (verifica listas de palavras restritas como "AUTOR", "AUTORAL").
- **Cruzamento e Score**: Realiza o match entre a autoria/ano extraída das chamadas em texto contra a lista de referências. Produz um payload tabular mapeando `'✅ OK'`, `'⚠️ ANO DIVERGENTE'`, `'❌ FALTA NA BIBLIOGRAFIA'` e `'ℹ️ SOBRANDO (NÃO CITADA)'`.

---

## Estrutura de Diretórios
```text
docentia/
│
├── main.py                      # Ponto de entrada e Interface Gráfica
├── ui_theme.py                  # Temas Dark Glass / Light Paper e carregador SVG
├── database.py                  # Manipulação do SQLite
├── validador_citacoes.py        # Motor Regex de validação ABNT
├── tcc_assistant.db             # Arquivo SQLite gerado localmente
├── iniciar.bat                  # Inicializador rápido para Windows (usa venv)
├── .env                         # Variáveis de ambiente locais (SMTP)
├── .env-example                 # Modelo de configuração SMTP
├── LICENSE                      # Licença MIT
├── README.md                    # Guia rápido
│
├── assets/                      # Logo, ícones SVG e ilustrações
│   ├── logo.svg
│   ├── icons/
│   └── illustrations/
│
└── docs/                        # Documentação de arquitetura, uso e migração Web
    ├── arquitetura.md
    ├── banco_de_dados.md
    ├── diagramas.md
    ├── HARNESS_WEB_MIGRATION.md
    ├── spec.md
    └── tutorial_uso_ui.md
```
