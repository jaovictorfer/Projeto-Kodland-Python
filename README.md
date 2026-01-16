# 🎮 Crazy Gravity Challenge (PgZero)

Crazy Gravity Challenge é um **jogo de plataforma 2D** desenvolvido em **Python com a biblioteca PgZero**.
O principal diferencial do jogo é a **inversão de gravidade**, utilizada para escapar dos inimigos e coletar orbes.

Este projeto foi desenvolvido como parte de um **processo seletivo**, seguindo restrições específicas de bibliotecas e boas práticas de código.

---

## 🕹️ Gameplay

* O jogador pode inverter a gravidade a qualquer momento
* Fantasmas surgem pelas laterais da tela e perseguem o jogador
* Os inimigos não desaparecem abruptamente: após um tempo, eles **saem da tela**
* Orbes aparecem no cenário e concedem pontos ao serem coletados

---

## ⌨️ Controles

* **← / →** — mover o personagem
* **Espaço** — inverter a gravidade
* **Clique do mouse** — interagir com o menu / voltar ao menu após o Game Over

---

## 🎯 Objetivo

Sobreviver o máximo de tempo possível e coletar o maior número de **orbes** sem tocar nos inimigos.

---

## 🚀 Como executar o jogo

### Pré-requisitos

* Python instalado
* PgZero instalado

### Executando pelo terminal (CMD)

```bat
cd projeto-kodland-python
pgzrun main.py
```

Ou, alternativamente:

```bat
python -m pgzero main.py
```

---

## ✨ Funcionalidades implementadas

* Menu principal com botões clicáveis:

  * Iniciar jogo
  * Ligar/Desligar música e sons
  * Sair
* Música de fundo contínua
* Efeitos sonoros (coleta de orbes e colisão)
* Inimigos com movimentação autônoma e perseguição contínua
* Animações de sprite:

  * Jogador parado
  * Jogador em movimento
  * Inimigos animados
* Mecânica de inversão de gravidade
* Barreiras laterais para evitar ataques fora da visão do jogador
* Código organizado, com classes, nomes claros e seguindo PEP8
* Uso exclusivo das bibliotecas permitidas: **PgZero**, `math` e `random`

---

## 📁 Estrutura do projeto

```
projeto-kodland-python/
│
├── main.py
├── images/
│   ├── player/
│   │   ├── player_idle_rd_0..10.png
│   │   ├── player_idle_ru_0..10.png
│   │   ├── player_idle_ld_0..10.png
│   │   ├── player_idle_lu_0..10.png
│   │   ├── player_walk_rd_0..11.png
│   │   ├── player_walk_ru_0..11.png
│   │   ├── player_walk_ld_0..11.png
│   │   └── player_walk_lu_0..11.png
│   │
│   └── enemy/
│       ├── enemy_right_0..9.png
│       └── enemy_left_0..9.png
│
├── music/
│   └── theme.ogg
│
└── sounds/
│   ├── orb.wav
│   └── hit.wav
```

---

## 📌 Observações

* Projeto desenvolvido **do zero** e é **100% autoral**
* Não utiliza diretamente a biblioteca Pygame
* Todas as animações utilizam **sprites animados reais**
* O foco do projeto é demonstrar lógica de jogo, organização de código e criatividade

---

## 👤 Autor

**João Victor Fernandes Cordeiro Martins**
