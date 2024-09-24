//App.js
import React, { useState, useRef } from 'react';
import GeminiRequest from './GeminiRequest.js'
import styles from '../CSS/App.module.css';

function App() {
  return(
    <div className={styles.all}>
      <GeminiRequest/>
    </div>
  )
}

export default App;