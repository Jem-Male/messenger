export const getData = async (URL) => {
    try {
        // 2. Добавили await. Теперь в response попадет реальный ответ, а не "Обещание"
        const response = await fetch(URL);
        
        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }
        
        // 3. Распарсить JSON тоже занимает время, поэтому тут тоже нужен await
        const data = await response.json();
        
        return data;
        
    } catch (error) {
        console.error("Произошла ошибка:", error);
    }
};