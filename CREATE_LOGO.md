# Instruções para Criar a Logo PCM

## Design da Logo

Baseado na imagem fornecida, a logo deve ter:

### Especificações

**Dimensões:**
- Largura: 800px
- Altura: 200px
- Formato: PNG com fundo transparente ou preto

**Cores:**
- Laranja: #ff7a00 (cor principal)
- Branco: #FFFFFF (texto)
- Preto: #000000 (fundo)

**Elementos:**
1. **Ícone X:** Grande "X" estilizado em laranja e branco (lado esquerdo)
2. **Texto Principal:** "PROXMOX" em branco com "MOX" em laranja
3. **Subtítulo:** "CENTER MANAGER" em branco, abaixo do texto principal
4. **Linha Separadora:** Linha horizontal fina em branco entre o texto e subtítulo

### Estrutura Visual

```
┌─────────────────────────────────────────────────┐
│                                                 │
│   ╱╲    PROX MOX                               │
│  ╱  ╲   ─────────────────                      │
│ ╱    ╲  CENTER MANAGER                         │
│                                                 │
└─────────────────────────────────────────────────┘
   ↑           ↑        ↑
Laranja/    Branco   Laranja
 Branco
```

## Como Criar

### Opção 1: Usando Figma/Adobe Illustrator

1. Criar novo documento 800x200px
2. Fundo preto (#000000)
3. Adicionar ícone X estilizado (laranja #ff7a00 e branco)
4. Texto "PROXMOX" - fonte bold/black
   - "PROX" em branco
   - "MOX" em laranja
5. Linha separadora horizontal
6. Texto "CENTER MANAGER" em branco
7. Exportar como PNG

### Opção 2: Usando Canva

1. Criar design personalizado 800x200px
2. Fundo preto
3. Adicionar formas para criar o X
4. Adicionar textos com as cores especificadas
5. Baixar como PNG

### Opção 3: Usando GIMP (Gratuito)

1. Novo arquivo 800x200px
2. Preencher com preto
3. Usar ferramenta de texto para adicionar "PROXMOX CENTER MANAGER"
4. Usar ferramenta de formas para criar o X
5. Exportar como PNG

## Instalação

Após criar a logo:

1. Salvar como `pcm-logo.png`
2. Copiar para o diretório `assets/`
3. Commit e push:

```bash
git add assets/pcm-logo.png
git commit -m "feat: add PCM logo"
git push
```

## Verificação

A logo aparecerá automaticamente no README.md em:
```
https://github.com/rsdenck/pcm
```

## Referência

A logo deve seguir o estilo da imagem fornecida:
- Profissional e enterprise
- Alto contraste (preto/branco/laranja)
- Legível em diferentes tamanhos
- Moderna e clean

## Nota Temporária

Atualmente o README está usando um placeholder. Substitua `assets/pcm-logo.png` pela logo real assim que criada.
