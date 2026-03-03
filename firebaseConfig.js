import { initializeApp } from 'firebase/app';
import { getDatabase } from 'firebase/database';

// ⚠️  PREENCHA COM AS SUAS CREDENCIAIS DO FIREBASE
// Veja o README.md para instruções de como criar o projeto no Firebase
const firebaseConfig = {
  apiKey: "SUA_API_KEY_AQUI",
  authDomain: "SEU_PROJETO.firebaseapp.com",
  databaseURL: "https://SEU_PROJETO-default-rtdb.firebaseio.com",
  projectId: "SEU_PROJETO",
  storageBucket: "SEU_PROJETO.appspot.com",
  messagingSenderId: "SEU_SENDER_ID",
  appId: "SEU_APP_ID"
};

const app = initializeApp(firebaseConfig);
export const db = getDatabase(app);
