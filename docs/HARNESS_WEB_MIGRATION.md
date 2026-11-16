# HARNESS DE IMPLEMENTAÇÃO: DOCENTIA WEB

> **Destinatário:** Agente de IA / Engenheiro de Software Autônomo  
> **Objetivo:** Implementar do zero a versão Web moderna, responsiva e de alta performance do **Docentia**, portando todas as capacidades da aplicação original Python/PyQt6 para a Stack **React + TypeScript + Vite + Vercel**, com **custo zero permanente**, persistência local no navegador (IndexedDB) e portabilidade total via arquivos JSON.

---

## 1. Visão Geral e Princípios Fundamentais

### 1.1. Propósito da Aplicação
O **Docentia Web** é uma Single Page Application (SPA) para professores, orientadores e membros de bancas examinadoras realizarem a revisão detalhada de Trabalhos de Conclusão de Curso (TCC) em PDF. Suas funcionalidades nucleares são:
1. **Dashboard de Projetos de Revisão**: CRUD completo de alunos, títulos, orientadores, status e histórico de revisões.
2. **Visualizador de PDF com Extração Interativa**: Leitura do PDF na tela com zoom, paginação e captura inteligente de trechos com o mouse (seleção por área/marquee ou texto), sincronizando instantaneamente com o painel de anotações.
3. **Painel de Anotações Acadêmicas**: Organização categorizada por cores (Apontamentos - Vermelho, Dúvida - Amarelo, Sugestão - Azul), com página, trecho citado e observações do professor.
4. **Parecer Geral com Auto-save**: Editor de parecer global com debounce automático de 2 segundos.
5. **Motor Científico de Validação de Citações ABNT**: Algoritmo client-side que processa o PDF, extrai a seção de "REFERÊNCIAS BIBLIOGRÁFICAS", busca citações no corpo do texto (formatos parentéticos e textuais), realiza cruzamento fuzzy (tolerância a pequenos erros de grafia) e classifica cada item como `OK`, `ANO DIVERGENTE`, `FALTA NA BIBLIOGRAFIA` ou `SOBRANDO (NÃO CITADA)`.
6. **Exportação de Relatórios Oficiais**: Geração no próprio navegador de relatórios em **PDF** (com assinatura estilizada em fonte cursiva), **Word (.docx)** formatado e planilhas de validação de citações em **Excel (.xlsx)** e **CSV**.
7. **Portabilidade & Soberania dos Dados (Zero Servidor)**: Todos os dados e arquivos PDF ficam salvos na máquina do usuário via **IndexedDB**. Um mecanismo robusto de **Exportação e Importação de Backup JSON** permite transferir tudo entre computadores sem depender de nuvens ou serviços pagos.

---

## 2. Restrições Arquiteturais & Filosofia "Zero Custo"

A IA executora **DEVE** seguir rigorosamente as restrições abaixo:

| Requisito | Diretriz Obrigatória |
| :--- | :--- |
| **Hospedagem / Deploy** | **Vercel** (Plano Hobby Gratuito). A aplicação é uma SPA 100% estática (Client-Side). Nenhuma função serverless com custo recorrente. |
| **Banco de Dados** | **Zero Cloud Database**. Proibido usar Supabase, Firebase, AWS RDS, Neon ou MongoDB Atlas pagos. Toda persistência primária ocorre no navegador via **IndexedDB** (usando `Dexie.js`). |
| **Armazenamento de PDFs** | Os PDFs enviados pelo usuário são armazenados localmente no IndexedDB como `Blob` ou `ArrayBuffer`. Nenhum arquivo vai para S3 ou bucket pago. |
| **Portabilidade Multi-máquina** | Sistema de **Exportação Completa (JSON/ZIP)** e **Restauração de Backup (JSON/ZIP)** com validação de integridade por schema, permitindo ao usuário migrar de máquina sem perder nada. |
| **Processamento de Citações** | 100% no navegador via Web Workers ou funções TypeScript/JavaScript, sem APIs pagas de IA ou servidores Python. |
| **Geração de Arquivos** | Client-side: `docx` para Word, `jspdf` / `html2canvas` para PDF, `xlsx` (SheetJS) para planilhas. |

---

## 3. Stack Tecnológica Recomendada

```
docentia-web/
├── Core: React 18+ com TypeScript
├── Bundler / Build Tool: Vite
├── Estilização: Tailwind CSS + Lucide React (Ícones)
├── Persistência Local: Dexie.js (Wrapper reativo sobre IndexedDB)
├── Motor de PDF: pdfjs-dist (Mozilla PDF.js)
├── Geração de Documentos: docx, jspdf, html2pdf.js, xlsx, file-saver
└── Utilitários de Comparação: fast-levenshtein (ou difflib.js)
```

---

## 4. Modelagem de Dados e Persistência Local (IndexedDB)

### 4.1. Esquema do Banco de Dados Local (`Dexie.js`)

O banco local deve ser nomeado `docentia_db`. Substitui com fidelidade o SQLite (`tcc_assistant.db`):

```typescript
// src/types/database.ts
export type ProjectStatus = 'Em Andamento' | 'Concluído' | 'Pendente';
export type AnnotationCategory = 'Apontamentos' | 'Dúvida' | 'Sugestão';

export interface Project {
  id?: number;                  // Chave primária auto-incrementada
  studentName: string;          // Nome do Aluno
  thesisTitle: string;          // Título do TCC
  advisorName?: string;         // Nome do Orientador
  advisorEmail?: string;        // E-mail do Orientador
  pdfFileName: string;          // Nome original do arquivo PDF
  pdfBlob?: Blob;               // Arquivo binário guardado localmente
  generalOpinion: string;       // Parecer Geral do Avaliador
  status: ProjectStatus;        // Status da Revisão
  createdAt: string;            // ISO String
  updatedAt: string;            // ISO String
}

export interface Annotation {
  id?: number;                  // Chave primária auto-incrementada
  projectId: number;            // FK para Project.id
  pageNumber: number;           // Número da página (1-based)
  selectedText: string;         // Trecho recortado/selecionado
  category: AnnotationCategory; // Categoria da anotação
  professorNotes: string;       // Comentários/observações do avaliador
  createdAt: string;            // ISO String
  updatedAt: string;            // ISO String
}

export interface CitationItem {
  id?: string;
  status: 'OK' | 'ANO DIVERGENTE' | 'FALTA NA BIBLIOGRAFIA' | 'SOBRANDO (NÃO CITADA)';
  citationFound: string;        // Ex: "(SILVA, 2020)"
  page: number | string;        // Número da página ou '-'
  context: string;              // Trecho de ~100 caracteres antes e depois
  referenceMatched: string;     // Referência bibliográfica correspondente
  author: string;
  year: string;
}

export interface AppSettings {
  id?: number;
  defaultEvaluatorName: string;
  theme: 'dark' | 'light';
  autoSaveDelayMs: number;
}
```

### 4.2. Definição do Dexie Database

```typescript
// src/db/index.ts
import Dexie, { Table } from 'dexie';
import { Project, Annotation, AppSettings } from '../types/database';

export class TCCDatabase extends Dexie {
  projects!: Table<Project, number>;
  annotations!: Table<Annotation, number>;
  settings!: Table<AppSettings, number>;

  constructor() {
    super('docentia_db');
    this.version(1).stores({
      projects: '++id, studentName, thesisTitle, status, updatedAt',
      annotations: '++id, projectId, pageNumber, category, createdAt',
      settings: '++id'
    });
  }
}

export const db = new TCCDatabase();
```

---

## 5. Estrutura do Sistema de Portabilidade (Backup JSON)

Para atender ao requisito mandatório de **troca de máquina sem perda de dados**, a IA deve implementar um módulo dedicado de importação e exportação.

### 5.1. Formato do Pacote de Backup (`.tccbak` ou `.json`)

```typescript
// src/types/backup.ts
export interface TCCBackupPayload {
  version: '1.0';
  exportedAt: string;
  application: 'Docentia Web';
  projects: Array<Omit<Project, 'pdfBlob'> & {
    pdfBase64?: string; // Opcional: permite portar o PDF embutido em Base64
  }>;
  annotations: Annotation[];
  settings?: AppSettings;
}
```

### 5.2. Casos de Uso de Portabilidade
1. **Backup Completo Leve (Sem PDF binário)**: Exporta todos os metadados, anotações e pareceres. Ao abrir em outra máquina, caso o usuário queira visualizar o PDF original novamente, a interface oferece um botão rápido: *"Vincular arquivo PDF local"*.
2. **Backup Completo com PDFs (Empacotado)**: Converte os Blobs locais para Base64 (ou cria um arquivo `.zip` via `JSZip`) contendo o `data.json` e a pasta de PDFs.
3. **Restauração com Confirmação e Merge/Substituição**: Ao importar, o usuário pode escolher entre **Substituir tudo** ou **Mesclar com os projetos existentes**.

---

## 6. Port do Motor de Validação de Citações ABNT (Python -> TypeScript)

A IA executora deve portar com precisão o algoritmo do arquivo `validador_citacoes.py`. Abaixo está a especificação algorítmica exata:

### 6.1. Extração de Texto com PDF.js

```typescript
// src/services/pdfExtractor.ts
import * as pdfjsLib from 'pdfjs-dist';

// Configurar worker do PDF.js para Vite
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url
).toString();

export async function extractPagesText(pdfBlob: Blob): Promise<string[]> {
  const arrayBuffer = await pdfBlob.arrayBuffer();
  const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
  const pages: string[] = [];

  for (let i = 1; i <= pdfDoc.numPages; i++) {
    const page = await pdfDoc.getPage(i);
    const textContent = await page.getTextContent();
    const pageString = textContent.items
      .map((item: any) => item.str)
      .join(' ');
    pages.push(pageString);
  }
  return pages;
}
```

### 6.2. Localização da Seção de Referências

1. **Varredura Reversa**: Percorrer as páginas do fim para o início procurando pelo cabeçalho `REFERÊNCIAS` ou `REFERÊNCIAS BIBLIOGRÁFICAS` (evitando correspondência precoce no Sumário).
2. **Fallback**: Se não encontrar no final, buscar nas últimas 30% das páginas.
3. **Corte de Anexos**: Se o texto após o início das referências contiver `ANEXO` ou `APÊNDICE`, truncar o texto para não interpretar anexos como bibliografia.
4. **Divisão de Referências Individuais**:
   - Padrão 1: quebra por linhas duplas (`\n\s*\n`).
   - Fallback ABNT: detectar quebras que iniciem com 2+ palavras em letras maiúsculas (`^[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}`).

### 6.3. Identificação de Citações no Corpo do Texto

Duas expressões regulares principais devem ser compiladas:

1. **Citações Parentéticas**: `\(\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ\s,;&\-]+?)(?:\s+et\s+al\.)?\s*,\s*(\d{4})[a-z]?(?:\s*,\s*p\.\s*\d+|\s*,\s*\d+|\s*:\s*\d+)?\s*\)`  
   *Exemplo*: `(SILVA, 2021)`, `(SANTOS; OLIVEIRA, 2019, p. 45)`

2. **Citações Textuais**: `\b([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zà-úâêôãõç]+(?:\s+(?:Filho|Neto|Júnior|Sobrinho))?(?:\s*,\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zà-úâêôãõç]+(?:\s+(?:Filho|Neto|Júnior|Sobrinho))?)*(?:\s+e\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zà-úâêôãõç]+(?:\s+(?:Filho|Neto|Júnior|Sobrinho))?|\s+et\s+al\.)?)\s*\(\s*(\d{4})[a-z]?(?::\s*\d+|,\s*p\.\s*\d+|\s+p\.\s*\d+)?\s*\)`  
   *Exemplo*: `Segundo Pressman (2010)`, `Para Booch, Rumbaugh e Jacobson (2005)`

3. **Lista de Exclusão (Stopwords / Falsos Positivos)**:  
   Ignorar se o autor for: `AUTOR`, `AUTORES`, `AUTORAL`, `O AUTOR`, `OS AUTORES`, `A AUTORA`, `AS AUTORAS`, `PRÓPRIO AUTOR`, `PRÓPRIOS AUTORES`, `PRÓPRIA AUTORA`, `DO AUTOR`, `DOS AUTORES`, `ELABORADO PELO AUTOR`, `FONTE`.

### 6.4. Cruzamento e Similaridade Fuzzy (Substituindo `difflib`)

Para simular o `difflib.SequenceMatcher(ratio >= 0.8)`:
```typescript
// src/services/stringSimilarity.ts
export function calculateSimilarity(s1: string, s2: string): number {
  const longer = s1.length > s2.length ? s1 : s2;
  const shorter = s1.length > s2.length ? s2 : s1;
  if (longer.length === 0) return 1.0;
  
  // Distância de Levenshtein
  const costs: number[] = [];
  for (let i = 0; i <= longer.length; i++) {
    let lastValue = i;
    for (let j = 0; j <= shorter.length; j++) {
      if (i === 0) costs[j] = j;
      else if (j > 0) {
        let newValue = costs[j - 1];
        if (longer.charAt(i - 1) !== shorter.charAt(j - 1)) {
          newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
        }
        costs[j - 1] = lastValue;
        lastValue = newValue;
      }
    }
    if (i > 0) costs[shorter.length] = lastValue;
  }
  return (longer.length - costs[shorter.length]) / longer.length;
}
```

---

## 7. Componentes e Telas da Aplicação

### 7.1. Dashboard Principal (`/` ou Estado Inicial)
- **Header**: Logotipo SVG do app + título "Docentia", botão de **Alternância de Tema (Modo Claro / Modo Escuro)** persistido em `AppSettings.theme`, e botões de Ações Globais:
  - 📥 **Importar Backup (JSON)**
  - 📤 **Exportar Backup (JSON)**
  - ➕ **Nova Revisão**
- **Cards de Métricas**: Total de Projetos, Em Andamento, Concluídos (cada um com ícone SVG dedicado).
- **Tabela de Projetos & Empty State Ilustrado**:
  - Colunas: Aluno, Título do TCC, Orientador, Status (badge com ícone e cor), Última Atualização, Ações.
  - Ações por linha: **Abrir Workspace**, **Editar Metadados**, **Alterar Status**, **Excluir** (com confirmação modal).
  - Campo de busca textual por Aluno ou Título.
  - Quando não houver projetos cadastrados (ou na busca sem resultados), exibir **ilustração SVG de estado vazio** centralizada com botão de chamada para *Nova Revisão*.

### 7.2. Modal "Nova Revisão"
- Campos:
  - Nome do Aluno (obrigatório)
  - Título do TCC (obrigatório)
  - Nome do Orientador (opcional)
  - E-mail do Orientador (opcional)
  - **Upload do Arquivo PDF**: Dropzone ilustrada (ícone/miniatura SVG de upload de PDF) com validação do tipo MIME `application/pdf`. O arquivo é gravado no IndexedDB sem upload externo.

### 7.3. Workspace de Revisão (`/workspace/:id`)
Interface dividida em duas colunas responsivas com divisor redimensionável (ex: `react-resizable-panels`), com barra superior compacta contendo botão **Voltar ao Painel**, resumo do projeto e **Alternância de Tema (Claro / Escuro)**:

#### Coluna Esquerda: Visualizador de PDF (65% largura padrão)
- **Barra de Ferramentas Superior**:
  - Zoom Out (`-`) / Zoom In (`+`) / Ajustar à Largura / 100% (com ícones SVG padronizados `lucide-react`)
  - Navegação de Página: Anterior (`<`), Próxima (`>`), input numérico `Página atual / Total` com salto imediato.
  - Alternador de Modo: Modo Leitura vs. Modo Seleção de Área (Rubber Band / Marquee).
- **Área de Canvas/Visualização**:
  - Renderiza a página via PDF.js sobre fundo neutro adaptado ao tema (`#0f172a` no escuro, `#e2e8f0` no claro para destacar a página branca).
  - Caso nenhum PDF esteja vinculado ou falhe ao carregar, exibe um card com **ilustração SVG de placeholder** e opção para vincular o arquivo.
  - Suporta seleção nativa de texto OU seleção de área retangular com o mouse. Ao soltar a seleção, o texto capturado e a página atual são transferidos imediatamente para o formulário de anotação na coluna direita.

#### Coluna Direita: Painel de Anotações e Parecer (35% largura padrão)
- **Card de Informações**: Nome do Aluno, Título do TCC, Orientador e link rápido para voltar ao Dashboard.
- **Abas de Categoria Coloridas**:
  - 🔴 **Apontamentos** (`#ef4444`)
  - 🟡 **Dúvida** (`#eab308`)
  - 🔵 **Sugestão** (`#3b82f6`)
- **Formulário de Anotação**:
  - Campo "Página" (preenchido automaticamente).
  - Campo "Trecho Citado" (textarea somente texto, preenchido automaticamente pela seleção).
  - Campo "Observações e Sugestões do Professor" (textarea com foco automático).
  - Botões: "Salvar Anotação" (ou "Atualizar"), "Cancelar Edição".
- **Lista de Anotações Cadastradas**:
  - Lista/Cards com badge de página, categoria colorida e trecho resumido.
  - Ações: Editar (carrega de volta no formulário) e Excluir.
- **Seção "Parecer Geral"**:
  - Textarea expansível com indicador discreto: `✅ Salvo automaticamente` / `⏳ Salvando...`.
  - Debounce de 2000ms salvando direto no IndexedDB.
- **Barra de Ações Finais**:
  - 📑 **Validar Citações ABNT**: Abre a modal de relatório analítico.
  - 📄 **Exportar Relatório**: Abre modal de exportação (PDF ou DOCX).
  - ✉️ **Enviar ao Orientador**: Dispara o fluxo de envio/compartilhamento.
  - 💾 **Salvar e Sair**: Retorna ao painel.

### 7.4. Modal de Validação de Citações ABNT
- Exibe resumo estatístico: total de citações detectadas, conformes, divergentes e referências não citadas.
- Tabela interativa com filtros rápidos por status (`Todas`, `OK`, `Avisos`, `Falta na Bibliografia`).
- Possibilidade de editar uma linha (caso o professor deseje corrigir manualmente um falso positivo) ou excluir.
- Botão **Exportar para Excel (.xlsx)** e **Exportar para CSV** (usando SheetJS / `xlsx` no client-side).

### 7.5. Modal de Exportação de Relatório
- Formulário:
  - Nome do Avaliador (ex: *Prof. Dr. João Silva*)
  - Data da Avaliação (padrão: data atual formatada `DD/MM/AAAA`)
  - Escolha de Formato: **PDF (.pdf)** ou **Word (.docx)**
- **Geração de DOCX**:
  - Utiliza o pacote `docx` no browser.
  - Estrutura idêntica à versão Python: Título principal, dados do aluno, bloco com cada anotação dividida por nível 2, parecer geral e rodapé centralizado com linha de assinatura e nome do avaliador estilizado.
- **Geração de PDF**:
  - Utiliza `html2pdf.js` ou `@react-pdf/renderer` para renderizar a folha A4 com margens de 15mm, tipografia limpa, tabela de anotações e assinatura com fonte cursiva (*Lucida Handwriting* ou *Great Vibes* via Google Fonts).

### 7.6. Envio por E-mail sem Servidor Pago
Como navegadores não executam conexões SMTP diretas (`smtplib`) por razões de segurança, a IA deve prover duas abordagens elegantes e 100% gratuitas:
1. **Opção Principal: Link `mailto:` Inteligente**:
   - Gera e baixa os arquivos do relatório (`.docx`/`.pdf` e `.xlsx`) diretamente para a pasta Downloads da máquina do usuário.
   - Abre o cliente de e-mail padrão do sistema (Outlook, Gmail, Thunderbird) pré-preenchido com destinatário (`advisor_email`), assunto padronizado e corpo com instrução clara para anexar os arquivos recém-baixados.
2. **Opção Complementar (EmailJS / Web Share)**:
   - Se o navegador suportar `navigator.share({ files: [...] })`, permite compartilhar os relatórios diretamente com um clique.
   - Configuração opcional de chaves gratuitas do EmailJS no painel de configurações para envio direto caso o usuário deseje.

---

## 8. Design System & Estética Visual

A aplicação deve oferecer suporte completo a **dois temas** alternáveis em tempo real (com persistência em `AppSettings.theme` no IndexedDB), mantendo equilíbrio visual e uso pontual de imagens/ilustrações sem poluir a área de leitura:

- **Tema Escuro — Dark Glassmorphism (Padrão)**:
  - Fundo principal: `#0b0f19` (Dark Slate / Deep Navy) e fundo do leitor de PDF em `#0f172a`.
  - Superfícies / Cards: `rgba(255, 255, 255, 0.03)` com bordas sutis `rgba(255, 255, 255, 0.08)` e efeito `backdrop-blur-md`.
  - Texto principal: `#e2e8f0`, secundário `#94a3b8`.
- **Tema Claro — Academic Paper**:
  - Fundo principal: `#f4f6fa` (papel suave para conforto visual) e fundo do leitor de PDF em `#e2e8f0`.
  - Superfícies / Cards: `#ffffff` com bordas sutis `#e2e8f0`.
  - Texto principal: `#0f172a`, secundário `#64748b`.
  - Abas selecionadas e badges devem adaptar contraste de texto para escuro (`#0f172a`) sobre fundos translúcidos claros.
- **Cores funcionais de destaque (compartilhadas entre ambos os temas)**:
  - Verde Esmeralda (`#10b981`): Botões de criação, confirmação, status concluído e exportação.
  - Azul Royal (`#3b82f6`): Ações primárias, navegação e abas de sugestão.
  - Laranja/Âmbar (`#f97316`): Ações de status, avisos e status em andamento.
  - Vermelho Carmim (`#ef4444`): Apontamentos críticos e exclusão.
- **Uso Equilibrado de Imagens e Ícones SVG**:
  - Logotipo vetorial próprio no cabeçalho do Dashboard e favicon.
  - Ícones vetoriais limpos (`lucide-react` / SVGs locais) em todos os botões de ação, barra do PDF, abas de categoria e indicadores de status/validação (sem uso de emojis crus em controles).
  - Ilustrações SVG estratégicas (fundo transparente para funcionar nos dois temas) em 3 pontos: **Empty State do Dashboard**, **Placeholder de PDF ausente/não carregado** e **Dropzone de upload de PDF**.
- **Tipografia**: Google Fonts **Inter** para a interface geral e uma fonte cursiva elegante (**Caveat** ou **Dancing Script**) para a assinatura digital do avaliador.
- **Micro-interações**: Efeitos hover suaves, transições de abas e tema, spinners de carregamento durante a extração do PDF e toasts de feedback (via `sonner` ou `react-hot-toast`).

---

## 9. Plano de Implementação Passo a Passo para a Nova IA

A IA executora deve realizar o desenvolvimento na seguinte sequência ordenada:

### Passo 1: Inicialização do Projeto
```bash
npm create vite@latest docentia-web -- --template react-ts
cd docentia-web
npm install
npm install dexie lucide-react clsx tailwindcss postcss autoprefixer pdfjs-dist docx file-saver xlsx
npx tailwindcss init -p
```

### Passo 2: Configuração do Banco Local (`Dexie.js`)
- Criar `src/types/database.ts` e `src/db/index.ts`.
- Criar hooks personalizados React para operações reativas (`useProjects`, `useAnnotations`, `useProjectDetails`).

### Passo 3: Serviço de Backup & Portabilidade
- Criar `src/services/backupService.ts` com funções `exportBackup(includePdfs: boolean)` e `importBackup(jsonString: string)`.
- Testar exportação e restauração de dados simulados.

### Passo 4: Motor de Validação ABNT em TypeScript
- Criar `src/services/citationValidator.ts` transcrevendo as Regex e a heurística de `validador_citacoes.py`.
- Criar testes unitários rápidos ou validação mock para garantir que casos como `(SILVA, 2020)`, `Souza (2018)` e falsos positivos de `Fonte: Autor (2022)` funcionem perfeitamente.

### Passo 5: Componente do Visualizador de PDF
- Criar `src/components/pdf/PdfViewer.tsx` utilizando `pdfjs-dist`.
- Suportar renderização em `<canvas>`, zoom in/out, navegação de páginas e evento de seleção com captura do texto e da página.

### Passo 6: Construção das Telas e Workflows
- `src/components/dashboard/ProjectList.tsx` e `NewProjectModal.tsx`.
- `src/components/workspace/Workspace.tsx` integrando o visualizador de PDF (lado esquerdo) e o painel de anotações (lado direito).
- Implementar formulário com abas coloridas, lista de anotações e Parecer Geral com auto-save.

### Passo 7: Geradores de Relatório (DOCX, PDF e Excel)
- `src/services/docxGenerator.ts` usando biblioteca `docx`.
- `src/services/pdfGenerator.ts` usando `jspdf` / `html2canvas` ou template HTML para impressão.
- `src/services/excelGenerator.ts` usando biblioteca `xlsx`.

### Passo 8: Deploy no Vercel
- Configurar `vite.config.ts` com base path correto e split de chunks.
- Adicionar `vercel.json` configurando rewrites de SPA:
  ```json
  {
    "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
  }
  ```
- Validar build sem erros de tipo TypeScript (`npm run build`).

---

## 10. Matriz de Paridade de Funcionalidades (Desktop vs. Web)

| Funcionalidade Original (Python/PyQt6) | Solução Equivalente Web (React + Vite) | Status |
| :--- | :--- | :--- |
| **Banco SQLite local** (`tcc_assistant.db`) | **IndexedDB** gerenciado via `Dexie.js` | 100% Client-Side |
| **Seleção de PDF via QFileDialog** | **File Input / Drag & Drop** com persistência do Blob no IndexedDB | 100% Client-Side |
| **Visualizador de PDF** (PyMuPDF `fitz` + QGraphicsView) | **Canvas PDF.js** (`pdfjs-dist`) com seleção por mouse/área | 100% Client-Side |
| **Categorias Coloridas** (QTabWidget) | **Abas com Tailwind CSS** e cores idênticas (#ef4444, #eab308, #3b82f6) | 100% Client-Side |
| **Auto-save do Parecer Geral** (QTimer 2s) | **Hook `useDebounce`** de 2s salvando no IndexedDB | 100% Client-Side |
| **Validador de Citações ABNT** (`validador_citacoes.py`) | **Engine TypeScript** (`citationValidator.ts`) com Regex e Levenshtein | 100% Client-Side |
| **Exportação Word (.docx)** (`python-docx`) | **Pacote `docx`** (JS) gerando `.docx` oficial e download direto | 100% Client-Side |
| **Exportação PDF** (`QPdfWriter`) | **Geração Client-Side** com `html2pdf.js` ou `@react-pdf/renderer` | 100% Client-Side |
| **Exportação Excel** (`pandas` / `openpyxl`) | **Pacote `xlsx` (SheetJS)** gerando planilhas `.xlsx` e `.csv` | 100% Client-Side |
| **Envio por E-mail** (`smtplib` SMTP) | **Protocolo `mailto:` pré-formatado** com anexos baixados localmente | 100% Gratuito |
| **Tema Claro / Escuro + Assets** (`ui_theme.py` + `app_settings` + `assets/`) | **Tailwind `dark:` / CSS Variables** + `AppSettings.theme` no IndexedDB + SVGs locais | 100% Client-Side |
| **Backup & Migração entre Máquinas** | **Exportação e Importação de Arquivo JSON** | 100% Autônomo |

---

## 11. Critérios de Aceite para Conclusão (Definition of Done)

A nova IA considerará a implementação concluída quando:
1. O comando `npm run build` executar sem nenhum erro ou aviso de lint crítico.
2. A aplicação for capaz de criar um novo projeto carregando um arquivo PDF de 50+ páginas sem travamentos.
3. O usuário conseguir navegar pelas páginas do PDF, selecionar trechos com o mouse e verificar o preenchimento automático da página e do texto no formulário de anotação.
4. Salvar, editar e excluir anotações nas três categorias (Apontamentos, Dúvida, Sugestão).
5. O parecer geral salvar automaticamente após 2 segundos de inatividade da digitação.
6. A validação de citações extrair a bibliografia e cruzar com as citações no texto, exibindo os resultados categorizados (`OK`, `DIVERGENTE`, `FALTA`, `SOBRANDO`).
7. Gerar e baixar os relatórios em `.docx`, `.pdf` e `.xlsx` com formatação profissional.
8. Alternar entre **Modo Claro** e **Modo Escuro** no Dashboard e no Workspace, mantendo legibilidade, contraste, ilustrações SVG e persistência da escolha após recarregar a página.
9. Realizar o download do backup em arquivo `.json`, limpar os dados do navegador (ou abrir em aba anônima), importar o `.json` e comprovar a restauração integral de todos os projetos e anotações.
