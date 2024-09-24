import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [photo, setPhoto] = useState(null);
  const [task, setTask] = useState('');
  const [response, setResponse] = useState(null);

  const handlePhotoChange = (e) => {
    setPhoto(e.target.files[0]);
  };

  const handleTaskChange = (e) => {
    setTask(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!photo || !task) {
      alert('Пожалуйста, загрузите фото и введите задачу.');
      return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(photo);
    reader.onloadend = async () => {
      const base64Photo = reader.result.split(',')[1];

      try {
        const res = await axios.post('https://d-art.site/gemini/process_image', {
          photo: base64Photo,
          task: task,
        });

        setResponse(res.data);
      } catch (error) {
        console.error('Ошибка при отправке запроса:', error);
        alert('Произошла ошибка при обработке запроса.');
      }
    };
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Отправка фото и задачи</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Загрузите фото:</label>
          <input type="file" accept="image/*" onChange={handlePhotoChange} />
        </div>
        <div style={{ marginTop: '10px' }}>
          <label>Введите задачу:</label>
          <input
            type="text"
            value={task}
            onChange={handleTaskChange}
            style={{ width: '300px' }}
          />
        </div>
        <button type="submit" style={{ marginTop: '10px' }}>
          Отправить
        </button>
      </form>

      {response && (
        <div style={{ marginTop: '20px' }}>
          <h2>Ответ от сервера:</h2>
          {response.error ? (
            <div>
              <p><strong>Ошибка:</strong> {response.error}</p>
              <p><strong>Сырой ответ:</strong> {response.raw_response}</p>
            </div>
          ) : (
            <div>
              <p><strong>About:</strong> {response.about}</p>
              <p><strong>Action:</strong> {response.action}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
