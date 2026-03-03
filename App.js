import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ActivityIndicator,
  Animated,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { StatusBar } from 'expo-status-bar';
import { ref, set, onValue } from 'firebase/database';
import { db } from './firebaseConfig';
import PixelCharacter from './components/PixelCharacter';

const USERS = {
  breno: { label: 'Breno', color: '#1D4ED8', lightColor: '#DBEAFE' },
  rosa:  { label: 'Rosa',  color: '#E91E8C', lightColor: '#FCE7F3' },
};

export default function App() {
  const [screen, setScreen] = useState('loading'); // 'loading' | 'select' | 'main'
  const [user, setUser] = useState(null);
  const [myMood, setMyMood] = useState('happy');
  const [partnerMood, setPartnerMood] = useState('happy');

  // Bounce animation for mood change
  const bounceAnim = useRef(new Animated.Value(1)).current;

  const triggerBounce = () => {
    Animated.sequence([
      Animated.spring(bounceAnim, { toValue: 1.2, useNativeDriver: true }),
      Animated.spring(bounceAnim, { toValue: 1.0, useNativeDriver: true }),
    ]).start();
  };

  useEffect(() => {
    AsyncStorage.getItem('selectedUser').then(saved => {
      if (saved && USERS[saved]) {
        setUser(saved);
        setScreen('main');
      } else {
        setScreen('select');
      }
    });
  }, []);

  useEffect(() => {
    if (!user) return;
    const partner = user === 'breno' ? 'rosa' : 'breno';

    const unsubMe = onValue(ref(db, `moods/${user}`), snap => {
      const val = snap.val();
      if (val === 'happy' || val === 'sad') setMyMood(val);
    });

    const unsubPartner = onValue(ref(db, `moods/${partner}`), snap => {
      const val = snap.val();
      if (val === 'happy' || val === 'sad') setPartnerMood(val);
    });

    return () => { unsubMe(); unsubPartner(); };
  }, [user]);

  const handleSelectUser = async (name) => {
    await AsyncStorage.setItem('selectedUser', name);
    await set(ref(db, `moods/${name}`), 'happy');
    setUser(name);
    setMyMood('happy');
    setScreen('main');
  };

  const handleMoodChange = async (mood) => {
    if (mood === myMood) return;
    triggerBounce();
    setMyMood(mood);
    await set(ref(db, `moods/${user}`), mood);
  };

  const handleLogout = async () => {
    await AsyncStorage.removeItem('selectedUser');
    setUser(null);
    setScreen('select');
  };

  if (screen === 'loading') {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#E91E8C" />
        <StatusBar style="dark" />
      </View>
    );
  }

  if (screen === 'select') {
    return <UserSelectScreen onSelect={handleSelectUser} />;
  }

  const partner = user === 'breno' ? 'rosa' : 'breno';

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <View style={styles.container}>

        {/* Header */}
        <Text style={styles.title}>Breno & Rosa</Text>
        <Text style={styles.subtitle}>Como vocês estão hoje?</Text>

        {/* Characters */}
        <View style={styles.charactersRow}>

          {/* Partner */}
          <View style={[styles.characterCard, { borderColor: USERS[partner].color }]}>
            <Text style={[styles.characterName, { color: USERS[partner].color }]}>
              {USERS[partner].label}
            </Text>
            <View style={styles.pixelWrapper}>
              <PixelCharacter character={partner} mood={partnerMood} pixelSize={8} />
            </View>
            <Text style={styles.moodEmoji}>
              {partnerMood === 'happy' ? '😊' : '😢'}
            </Text>
          </View>

          {/* Me */}
          <View style={[styles.characterCard, { borderColor: USERS[user].color }]}>
            <Text style={[styles.characterName, { color: USERS[user].color }]}>
              Você
            </Text>
            <Animated.View style={[styles.pixelWrapper, { transform: [{ scale: bounceAnim }] }]}>
              <PixelCharacter character={user} mood={myMood} pixelSize={8} />
            </Animated.View>
            <Text style={styles.moodEmoji}>
              {myMood === 'happy' ? '😊' : '😢'}
            </Text>
          </View>

        </View>

        {/* Mood buttons */}
        <Text style={styles.questionText}>Como você está?</Text>

        <TouchableOpacity
          style={[styles.moodBtn, myMood === 'happy' && styles.moodBtnActive, { borderColor: '#22C55E' }]}
          onPress={() => handleMoodChange('happy')}
          activeOpacity={0.8}
        >
          <Text style={styles.moodBtnIcon}>😊</Text>
          <Text style={[styles.moodBtnText, myMood === 'happy' && { color: '#22C55E' }]}>
            Alegre
          </Text>
          {myMood === 'happy' && <View style={[styles.activeDot, { backgroundColor: '#22C55E' }]} />}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.moodBtn, myMood === 'sad' && styles.moodBtnActive, { borderColor: '#6366F1' }]}
          onPress={() => handleMoodChange('sad')}
          activeOpacity={0.8}
        >
          <Text style={styles.moodBtnIcon}>😢</Text>
          <Text style={[styles.moodBtnText, myMood === 'sad' && { color: '#6366F1' }]}>
            Triste
          </Text>
          {myMood === 'sad' && <View style={[styles.activeDot, { backgroundColor: '#6366F1' }]} />}
        </TouchableOpacity>

        {/* Logout */}
        <TouchableOpacity onPress={handleLogout} style={styles.logoutBtn}>
          <Text style={styles.logoutText}>Trocar usuário</Text>
        </TouchableOpacity>

      </View>
    </SafeAreaView>
  );
}

function UserSelectScreen({ onSelect }) {
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <View style={styles.container}>
        <Text style={styles.title}>Breno & Rosa</Text>
        <Text style={styles.subtitle}>Quem é você?</Text>

        <View style={styles.selectRow}>
          {Object.entries(USERS).map(([key, info]) => (
            <TouchableOpacity
              key={key}
              style={[styles.selectCard, { borderColor: info.color, backgroundColor: info.lightColor }]}
              onPress={() => onSelect(key)}
              activeOpacity={0.85}
            >
              <View style={styles.pixelWrapper}>
                <PixelCharacter character={key} mood="happy" pixelSize={9} />
              </View>
              <Text style={[styles.selectName, { color: info.color }]}>{info.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FFF0F5',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFF0F5',
  },
  container: {
    flex: 1,
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 24,
  },

  // Header
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: '#1A1A1A',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 15,
    color: '#666',
    marginBottom: 28,
  },

  // Characters row
  charactersRow: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 32,
  },
  characterCard: {
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 2,
    paddingVertical: 16,
    paddingHorizontal: 12,
    width: 148,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
  },
  characterName: {
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 10,
    letterSpacing: 0.3,
  },
  pixelWrapper: {
    marginBottom: 10,
  },
  moodEmoji: {
    fontSize: 22,
  },

  // Question
  questionText: {
    fontSize: 17,
    fontWeight: '600',
    color: '#333',
    marginBottom: 14,
  },

  // Mood buttons
  moodBtn: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    paddingVertical: 14,
    paddingHorizontal: 20,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 1 },
    elevation: 2,
  },
  moodBtnActive: {
    backgroundColor: '#FAFAFA',
  },
  moodBtnIcon: {
    fontSize: 24,
    marginRight: 14,
  },
  moodBtnText: {
    fontSize: 17,
    fontWeight: '600',
    color: '#555',
    flex: 1,
  },
  activeDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },

  // Logout
  logoutBtn: {
    marginTop: 20,
    padding: 8,
  },
  logoutText: {
    fontSize: 13,
    color: '#999',
    textDecorationLine: 'underline',
  },

  // User select
  selectRow: {
    flexDirection: 'row',
    gap: 20,
    marginTop: 8,
  },
  selectCard: {
    alignItems: 'center',
    borderRadius: 20,
    borderWidth: 2,
    paddingVertical: 20,
    paddingHorizontal: 16,
    width: 150,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
  },
  selectName: {
    fontSize: 18,
    fontWeight: '800',
    marginTop: 12,
    letterSpacing: 0.3,
  },
});
