<div align="center">

<img src="assets/logo.svg" alt="Docentia Logo" width="88" height="88" />

# Docentia

**Plataforma desktop inteligente para revisão acadêmica de Trabalhos de Conclusão de Curso (TCC)**

Leitura interativa de PDFs, captura instantânea de trechos, validação automatizada de citações ABNT, temas Claro & Escuro e exportação profissional de pareceres.

<p>
  <a href="#-demonstração-em-vídeo">Demonstração</a> •
  <a href="#-funcionalidades">Funcionalidades</a> •
  <a href="#-design--temas">Design & Temas</a> •
  <a href="#-instalação-e-execução">Instalação</a> •
  <a href="#-estrutura-do-projeto">Arquitetura</a> •
  <a href="#-documentação">Documentação</a> •
  <a href="#-licença-mit">Licença</a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/GUI-PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6" />
  <img src="https://img.shields.io/badge/PDF-PyMuPDF-EF4444?style=for-the-badge&logo=adobeacrobatreader&logoColor=white" alt="PyMuPDF" />
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="MIT License" />
  </a>
</p>

</div>

---

## ✦ Visão Geral

O **Docentia** foi projetado para professores, orientadores e membros de bancas examinadoras que precisam revisar trabalhos acadêmicos com **agilidade, precisão e organização**. Em um único workspace dividido (65% leitura / 35% avaliação), você lê o PDF, destaca trechos diretamente com o mouse, verifica automaticamente a conformidade das citações com a bibliografia e gera o parecer final pronto para entrega.

---

## 🎬 Demonstração em Vídeo

Veja em menos de 40 segundos o fluxo completo de revisão no Docentia (painel inicial, captura de trechos no PDF, anotações, parecer com auto-save, validador ABNT, modo claro e exportação):

https://github.com/user-attachments/assets/dd571edc-78fb-4f84-b99d-9e6cb0b1cdea

---

## ◈ Funcionalidades

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>📄 Visualizador de PDF Interativo</h3>
      <p>Renderização de alta nitidez com zoom, navegação rápida por página e seleção retangular (<em>Rubber Band</em>): basta arrastar o mouse sobre um trecho para preencher automaticamente o número da página e o texto citado no painel de anotações.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🏷️ Anotações & Parecer Auto-save</h3>
      <p>Organize observações por categoria visual — <strong>Apontamentos</strong>, <strong>Dúvida</strong> e <strong>Sugestão</strong> — com edição rápida em tabela e redação de Parecer Geral com salvamento automático a cada 2 segundos.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🔍 Validador Científico ABNT</h3>
      <p>Motor de análise que localiza a seção de Referências, extrai citações parentéticas <code>(AUTOR, 2024)</code> e textuais <code>Autor (2024)</code>, aplica correspondência <em>fuzzy</em> e aponta itens conformes, divergentes, faltantes ou não citados.</p>
    </td>
    <td width="50%" valign="top">
      <h3>📊 Exportação Multi-formato</h3>
      <p>Exporte relatórios completos em <strong>PDF (.pdf)</strong> e <strong>Word (.docx)</strong> com assinatura estilizada em fonte cursiva, além de planilhas de validação de citações em <strong>Excel (.xlsx)</strong> e <strong>CSV</strong>.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🌓 Modo Escuro & Modo Claro</h3>
      <p>Alterne em um clique entre o elegante tema <strong>Dark Glassmorphism</strong> e o confortável <strong>Light Academic Paper</strong>, com preferência salva automaticamente no banco local.</p>
    </td>
    <td width="50%" valign="top">
      <h3>✉️ Envio Direto ao Orientador</h3>
      <p>Gere o parecer e a planilha de citações e envie ambos automaticamente em anexo para o e-mail do orientador via SMTP configurado diretamente na interface (ou no arquivo <code>.env</code>).</p>
    </td>
  </tr>
</table>

---

## ✦ Design & Temas

A interface combina produtividade acadêmica com acabamento visual moderno:

| Característica | Modo Escuro (`Dark Glass`) | Modo Claro (`Academic Paper`) |
| :--- | :--- | :--- |
| **Fundo & Superfícies** | Ardósia profunda (`#0b0f19`) com painéis translúcidos | Papel suave (`#f4f6fa`) com cartões limpos (`#ffffff`) |
| **Leitor de PDF** | Moldura escura (`#0f172a`) para foco em leitura noturna | Moldura neutra (`#e2e8f0`) para destaque da folha branca |
| **Iconografia & Imagens** | Ícones vetoriais SVG sob medida e ilustrações de estado vazio | Adaptação automática de contraste e badges por categoria |
| **Persistência** | Salvo na tabela `app_settings` do SQLite local | Mantido entre sessões ao fechar e reabrir o aplicativo |

---

## ◈ Instalação e Execução

### 📦 Opção 1 — Baixar Versão Pronta *(Mais fácil: Windows, macOS e Linux)*

Você **não** precisa instalar Python nem digitar comandos. Basta acessar a página de [**Releases no GitHub**](https://github.com/maromo71/docentia/releases) e baixar o arquivo do seu sistema:

- **Windows:** baixe **`Docentia-Setup-Windows.exe`** *(instalador padrão)* ou **`Docentia-Windows-Portable.zip`** *(extrair e abrir `Docentia.exe`)*.
  > *Se aparecer o aviso "O Windows protegeu o computador", clique em **Mais informações** → **Executar assim mesmo**.*
- **macOS (Apple Silicon M1/M2/M3/M4):** baixe **`Docentia-macOS-arm64.dmg`**, abra o arquivo e arraste o **Docentia** para a pasta **Aplicativos**.
  > *Na primeira abertura, caso o macOS exiba aviso de desenvolvedor não verificado, vá em **Ajustes do Sistema → Privacidade e Segurança → Abrir Mesmo Assim**.*
- **Linux (x86_64):** baixe **`Docentia-Linux-x86_64.tar.gz`**, extraia a pasta e execute `./Docentia` *(ou rode `./instalar-atalho.sh` para criar atalho no menu de aplicativos)*.

---

### 🚀 Opção 2 — Instalação via Código-fonte no Windows *(2 cliques)*

Se preferir rodar diretamente pelo código-fonte em Python:

1. **Instale o Python** *(se ainda não tiver no computador)*
   - Baixe a versão mais recente em [python.org/downloads](https://www.python.org/downloads/).
   - **ATENÇÃO:** na **primeira tela** do instalador, **marque a caixinha `"Add python.exe to PATH"`** antes de clicar em *Install Now*.

2. **Baixe o Docentia**
   - No topo desta página do GitHub, clique no botão verde **`<> Code`** → **`Download ZIP`** e extraia o arquivo.

3. **Execute o instalador automático**
   - Abra a pasta extraída e dê **dois cliques em [`instalar.bat`](instalar.bat)**.
   - Quando aparecer **`Instalacao concluida com sucesso!`**, feche a janela.

4. **Abra o programa no dia a dia**
   - Sempre que quiser usar o Docentia, basta dar **dois cliques em [`iniciar.bat`](iniciar.bat)**.

---

### ✉️ Configurar o envio de e-mail com Gmail *(opcional)*

Você pode configurar tudo **dentro do próprio aplicativo**, sem precisar editar arquivos ocultos:

1. Acesse sua Conta Google e ative a **Verificação em duas etapas** na aba *Segurança*.
2. Entre em [**Senhas de App do Google**](https://myaccount.google.com/apppasswords), digite um nome (ex.: `Docentia`) e clique em **Criar**. Copie o código de **16 letras** gerado.
3. Abra o **Docentia**, clique no botão **`Configurar E-mail`** no topo do Painel Inicial, deixe o provedor **Gmail (Google)** selecionado, informe seu e-mail, cole a **Senha de App de 16 letras** e clique em **Testar Conexão** → **Salvar**.

> **Importante:** A senha comum do Gmail **não** funciona no envio automático; use sempre a **Senha de App**. *(Desenvolvedores que preferirem usar `.env` podem copiar `.env-example` para `.env`, que continua funcionando como fallback.)*

---

### 🛟 Problemas comuns (Solução rápida)

- **Aviso de segurança ao abrir no Windows ou macOS:** ocorre porque o instalador comunitário não possui certificado pago de assinatura; basta autorizar uma única vez conforme indicado na Opção 1.
- **"Python não encontrado" ao rodar `instalar.bat`:** execute novamente o instalador do Python e marque **`Add python.exe to PATH`** na primeira tela.
- **Erro ao enviar e-mail:** clique em **`Configurar E-mail`** no Painel, confirme o uso da **Senha de App de 16 letras** e clique em **Testar Conexão**.

<details>
<summary><strong>💻 Instalação Manual e Build Local (Desenvolvedores)</strong></summary>

1. **Clone o repositório**
   ```bash
   git clone https://github.com/maromo71/docentia.git
   cd docentia
   ```

2. **Crie e ative o ambiente virtual**
   ```bash
   python -m venv venv

   # Windows (Prompt de Comando - CMD)
   venv\Scripts\activate.bat

   # Linux / macOS
   source venv/bin/activate
   ```

3. **Instale as dependências e execute**
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

4. **Gerar build local com PyInstaller *(opcional)***
   ```bash
   pip install pyinstaller
   pyinstaller --clean --noconfirm docentia.spec
   ```

</details>

---

## ✦ Estrutura do Projeto

```text
docentia/
├── .github/workflows/
│   └── release.yml              # Pipeline GitHub Actions (Windows, Linux e macOS)
├── packaging/
│   ├── windows/docentia.iss     # Script do instalador Windows (Inno Setup)
│   └── linux/                   # Atalho .desktop e script de instalação no Linux
├── main.py                      # Interface gráfica PyQt6 (Dashboard, Workspace, Diálogos e Exportação)
├── ui_theme.py                  # Temas Dark Glass & Light Paper, tokens de cor e carregador SVG
├── database.py                  # Camada SQLite (projetos, anotações e configurações/SMTP)
├── validador_citacoes.py        # Motor de extração e cruzamento ABNT (Regex + SequenceMatcher)
├── assets/                      # Logo (.svg/.png/.ico), ícones SVG e ilustrações de interface
├── docs/                        # Documentação técnica, guia do usuário e especificação Web
│   └── HARNESS_WEB_MIGRATION.md # Especificação arquitetural para futura versão Web (React + Vite)
├── docentia.spec                # Especificação multiplataforma do PyInstaller
├── instalar.bat                 # Instalador automático em 2 cliques para Windows (via fonte)
├── iniciar.bat                  # Inicializador rápido para Windows (via fonte)
├── requirements.txt             # Lista de dependências Python do projeto
├── .env-example                 # Modelo opcional de configuração SMTP
└── LICENSE                      # Licença MIT
```

---

## ◈ Documentação

Explore a pasta `docs/` para detalhes técnicos completos e guias de utilização:

| Documento | Conteúdo |
| :--- | :--- |
| [docs/arquitetura.md](docs/arquitetura.md) | Estrutura modular, responsabilidades e tecnologias utilizadas |
| [docs/banco_de_dados.md](docs/banco_de_dados.md) | Modelagem de dados e esquema do banco SQLite |
| [docs/diagramas.md](docs/diagramas.md) | Fluxogramas e diagramas de sequência da aplicação |
| [docs/tutorial_uso_ui.md](docs/tutorial_uso_ui.md) | Guia passo a passo focado no usuário final |
| [docs/HARNESS_WEB_MIGRATION.md](docs/HARNESS_WEB_MIGRATION.md) | Especificação completa para portar o projeto para Web 100% client-side |

---

## ◈ Licença (MIT)

Este projeto é distribuído sob a **Licença MIT** — consulte o arquivo [`LICENSE`](LICENSE) para o texto integral.

Em resumo, você tem **liberdade total** para:
- ✅ **Usar** livremente para fins pessoais, acadêmicos ou comerciais
- ✅ **Modificar** o código-fonte e adaptar às suas necessidades
- ✅ **Distribuir e comercializar** versões originais ou modificadas, incluindo obtenção de lucro
- ℹ️ Mantendo apenas o aviso de direitos autorais e a cópia da licença MIT nos arquivos redistribuídos

---

<div align="center">
  <sub>Desenvolvido para elevar a precisão, a agilidade e a clareza em revisões e bancas de TCC.</sub>
</div>
