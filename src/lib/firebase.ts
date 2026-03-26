import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyDBd7yqIK7oXMWbsRhagZMvP8ldDMgO1Uw",
  authDomain: "jumhadi.firebaseapp.com",
  projectId: "jumhadi",
  storageBucket: "jumhadi.firebasestorage.app",
  messagingSenderId: "413295646804",
  appId: "1:413295646804:web:adaa8dd9cfb1f03fe1b5c1",
  measurementId: "G-MFH6ZMV40K",
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
