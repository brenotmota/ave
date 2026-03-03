import React from 'react';
import { View, StyleSheet } from 'react-native';

// Color palette
const SKIN = '#FFCBA4';
const EYE  = '#1A1A1A';
const BLSH = '#FFB6C1';
const MOUT = '#C43C3C';
const B_HR = '#2D1B00'; // Breno: dark brown hair
const B_BD = '#1D4ED8'; // Breno: blue shirt
const B_PT = '#1E3A5F'; // Breno: dark navy pants
const R_HR = '#FF69B4'; // Rosa: hot pink hair
const R_BD = '#E91E8C'; // Rosa: deep pink shirt
const R_SK = '#9B2C6C'; // Rosa: dark pink skirt
const ____ = null;      // transparent

const BRENO_HAPPY = [
  [____, B_HR, B_HR, B_HR, B_HR, B_HR, B_HR, ____, ____, ____],
  [____, B_HR, B_HR, B_HR, B_HR, B_HR, B_HR, B_HR, ____, ____],
  [____, B_HR, SKIN, SKIN, SKIN, SKIN, SKIN, B_HR, ____, ____],
  [____, SKIN, SKIN, EYE,  SKIN, SKIN, EYE,  SKIN, ____, ____],
  [____, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, ____, ____],
  [____, SKIN, BLSH, SKIN, SKIN, SKIN, BLSH, SKIN, ____, ____],
  [____, SKIN, SKIN, MOUT, MOUT, MOUT, MOUT, SKIN, ____, ____],
  [____, ____, SKIN, SKIN, SKIN, SKIN, SKIN, ____, ____, ____],
  [B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD],
  [____, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, ____],
  [____, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, ____],
  [____, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, ____],
  [____, B_PT, B_PT, ____, ____, ____, ____, B_PT, B_PT, ____],
  [____, B_PT, B_PT, ____, ____, ____, ____, B_PT, B_PT, ____],
];

const BRENO_SAD = [
  [____, B_HR, B_HR, B_HR, B_HR, B_HR, B_HR, ____, ____, ____],
  [____, B_HR, B_HR, B_HR, B_HR, B_HR, B_HR, B_HR, ____, ____],
  [____, B_HR, SKIN, SKIN, SKIN, SKIN, SKIN, B_HR, ____, ____],
  [____, SKIN, SKIN, EYE,  SKIN, SKIN, EYE,  SKIN, ____, ____],
  [____, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, ____, ____],
  [____, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, ____, ____],
  [____, SKIN, MOUT, SKIN, SKIN, SKIN, SKIN, MOUT, ____, ____],
  [____, ____, SKIN, MOUT, MOUT, SKIN, SKIN, ____, ____, ____],
  [B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD],
  [____, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, ____],
  [____, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, ____],
  [____, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, B_BD, ____],
  [____, B_PT, B_PT, ____, ____, ____, ____, B_PT, B_PT, ____],
  [____, B_PT, B_PT, ____, ____, ____, ____, B_PT, B_PT, ____],
];

const ROSA_HAPPY = [
  [____, R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, ____, ____],
  [R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, ____],
  [____, R_HR, SKIN, SKIN, SKIN, SKIN, SKIN, R_HR, ____, ____],
  [____, SKIN, SKIN, EYE,  SKIN, SKIN, EYE,  SKIN, ____, ____],
  [____, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, ____, ____],
  [____, SKIN, BLSH, SKIN, SKIN, SKIN, BLSH, SKIN, ____, ____],
  [____, SKIN, SKIN, MOUT, MOUT, MOUT, MOUT, SKIN, ____, ____],
  [____, ____, SKIN, SKIN, SKIN, SKIN, SKIN, ____, ____, ____],
  [R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD],
  [____, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, ____],
  [____, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, ____],
  [____, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, ____],
  [____, R_SK, R_SK, R_SK, R_SK, R_SK, R_SK, R_SK, R_SK, ____],
  [____, R_SK, R_SK, ____, ____, ____, ____, R_SK, R_SK, ____],
];

const ROSA_SAD = [
  [____, R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, ____, ____],
  [R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, R_HR, ____],
  [____, R_HR, SKIN, SKIN, SKIN, SKIN, SKIN, R_HR, ____, ____],
  [____, SKIN, SKIN, EYE,  SKIN, SKIN, EYE,  SKIN, ____, ____],
  [____, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, ____, ____],
  [____, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, SKIN, ____, ____],
  [____, SKIN, MOUT, SKIN, SKIN, SKIN, SKIN, MOUT, ____, ____],
  [____, ____, SKIN, MOUT, MOUT, SKIN, SKIN, ____, ____, ____],
  [R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD],
  [____, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, ____],
  [____, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, ____],
  [____, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, R_BD, ____],
  [____, R_SK, R_SK, R_SK, R_SK, R_SK, R_SK, R_SK, R_SK, ____],
  [____, R_SK, R_SK, ____, ____, ____, ____, R_SK, R_SK, ____],
];

const PIXEL_DATA = {
  breno: { happy: BRENO_HAPPY, sad: BRENO_SAD },
  rosa:  { happy: ROSA_HAPPY,  sad: ROSA_SAD  },
};

export default function PixelCharacter({ character, mood, pixelSize = 9 }) {
  const grid = PIXEL_DATA[character]?.[mood] ?? PIXEL_DATA.breno.happy;

  return (
    <View style={styles.container}>
      {grid.map((row, rowIndex) => (
        <View key={rowIndex} style={styles.row}>
          {row.map((color, colIndex) => (
            <View
              key={colIndex}
              style={[
                styles.pixel,
                { width: pixelSize, height: pixelSize },
                color ? { backgroundColor: color } : { backgroundColor: 'transparent' },
              ]}
            />
          ))}
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'flex-start',
  },
  row: {
    flexDirection: 'row',
  },
  pixel: {
    // base pixel — color applied inline
  },
});
