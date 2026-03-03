# Breno & Rosa — App de Humor Pixel

App mobile para Breno e Rosa compartilharem seus humores em tempo real com personagens pixel art.

## Como funciona

- Cada um abre o app e seleciona quem é (Breno ou Rosa)
- Escolhe seu humor: **Alegre** ou **Triste**
- O personagem pixel muda de expressão instantaneamente
- O outro vê a mudança em tempo real no próprio celular

---

## Configuração (antes de rodar pela primeira vez)

### 1. Instalar dependências

```bash
npm install
```

### 2. Criar projeto no Firebase

1. Acesse [console.firebase.google.com](https://console.firebase.google.com)
2. Clique em **"Adicionar projeto"** e siga os passos
3. No menu lateral, vá em **Build → Realtime Database**
4. Clique em **"Criar banco de dados"**
5. Escolha a região (pode ser `us-central1`)
6. Em **Regras**, cole o seguinte e publique:

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

### 3. Pegar as credenciais do Firebase

1. No console, vá em **Configurações do projeto** (ícone de engrenagem)
2. Role até **"Seus apps"** e clique em **"</>  Web"**
3. Registre o app com qualquer nome
4. Copie o objeto `firebaseConfig` exibido

### 4. Preencher o arquivo `firebaseConfig.js`

Abra o arquivo `firebaseConfig.js` e substitua os valores:

```js
const firebaseConfig = {
  apiKey: "cole aqui",
  authDomain: "cole aqui",
  databaseURL: "cole aqui",   // <-- IMPORTANTE: precisa incluir o databaseURL
  projectId: "cole aqui",
  storageBucket: "cole aqui",
  messagingSenderId: "cole aqui",
  appId: "cole aqui"
};
```

> **Atenção:** o campo `databaseURL` não aparece automaticamente no firebaseConfig padrão.
> Você encontra ele no menu **Realtime Database → Dados**, no topo da tela, no formato:
> `https://SEU-PROJETO-default-rtdb.firebaseio.com`

---

## Rodando no celular (Expo Go)

### Opção A — Expo Go (mais fácil, sem publicar na loja)

1. Instale o app **Expo Go** no celular (Android ou iPhone)
2. No terminal, rode:

```bash
npx expo start
```

3. Escaneie o QR code com o Expo Go
4. O app abre diretamente — faça o mesmo no celular da Rosa

### Opção B — Build standalone (APK/IPA)

```bash
npx expo build:android
# ou
npx expo build:ios
```

---

## Estrutura do projeto

```
breno-rosa-mood/
├── App.js                  # Componente principal + telas
├── firebaseConfig.js       # Credenciais Firebase (preencher!)
├── components/
│   └── PixelCharacter.js   # Personagens pixel art
├── app.json                # Configuração Expo
└── package.json
```

## Dados no Firebase

```
moods/
  breno: "happy" | "sad"
  rosa:  "happy" | "sad"
```
