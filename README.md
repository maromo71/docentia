<div align="center">

<img src="assets/logo.svg" alt="Docentia Logo" width="88" height="88" />

# Docentia

**Plataforma desktop inteligente para revisão acadêmica de Trabalhos de Conclusão de Curso (TCC)**

Leitura interativa de PDFs, captura instantânea de trechos, validação automatizada de citações ABNT, temas Claro & Escuro e exportação profissional de pareceres.

<p>
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
      <p>Gere o parecer e a planilha de citações e envie ambos automaticamente em anexo para o e-mail do orientador via SMTP configurado localmente no arquivo <code>.env</code>.</p>
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

### Pré-requisitos
- **Python 3.9+** instalado na máquina

### Passo a passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/maromo71/docentia.git
   cd docentia
   ```

2. **Crie e ative um ambiente virtual** *(recomendado)*
   ```bash
   python -m venv venv

   # Windows (PowerShell / CMD)
   venv\Scripts\activate

   # Linux / macOS
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install PyQt6 PyMuPDF python-docx pandas openpyxl python-dotenv
   ```

4. **Configure o envio de e-mail *(opcional)***
   Copie o arquivo de exemplo `.env-example` para `.env` e preencha suas credenciais SMTP:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=seu-email@gmail.com
   SMTP_PASSWORD=sua-senha-de-app-de-16-digitos
   ```
   > **Dica:** Para contas Google/Gmail, utilize uma *Senha de App* gerada nas configurações de segurança da conta.

5. **Execute a aplicação**
   ```bash
   python main.py
   ```
   > No Windows, você também pode iniciar diretamente usando o atalho [`iniciar_tcc_analyzer.bat`](iniciar_tcc_analyzer.bat).

---

## ✦ Estrutura do Projeto

```text
docentia/
├── main.py                      # Interface gráfica PyQt6 (Dashboard, Workspace, Diálogos e Exportação)
├── ui_theme.py                  # Temas Dark Glass & Light Paper, tokens de cor e carregador SVG
├── database.py                  # Camada SQLite (projetos, anotações e preferências de tema)
├── validador_citacoes.py        # Motor de extração e cruzamento ABNT (Regex + SequenceMatcher)
├── assets/                      # Identidade visual, ícones SVG e ilustrações de interface
│   ├── logo.svg
│   ├── icons/
│   └── illustrations/
├── docs/                        # Documentação técnica e guia do usuário
├── HARNESS_WEB_MIGRATION.md     # Especificação arquitetural para futura versão Web (React + Vite)
├── iniciar_tcc_analyzer.bat     # Inicializador rápido para Windows
├── .env-example                 # Modelo de configuração SMTP
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
| [HARNESS_WEB_MIGRATION.md](HARNESS_WEB_MIGRATION.md) | Especificação completa para portar o projeto para Web 100% client-side |

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
