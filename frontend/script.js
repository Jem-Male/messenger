

// 1. Добавили слово async перед параметрами функции
const getData = async (URL) => {
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

const ChangeText = (ElmId, Data) => {
    let element = document.getElementById(ElmId);
    
    // API с котами возвращает массив объектов. 
    // Если мы просто вставим его в текст, будет написано [object Object].
    // Поэтому мы превращаем JSON-объект в красивую строку, чтобы посмотреть на него:
    element.textContent = JSON.stringify(Data, null, 2);
};

// 4. Поскольку getData теперь асинхронная, мы не можем просто написать res = getData().
// Нам нужно дождаться результата. Самый простой способ сделать это вне async функции — использовать .then()
getData("https://api.thecatapi.com/v1/images/search").then((res) => {
    // Этот блок кода выполнится ТОЛЬКО тогда, когда данные прилетят с сервера
    ChangeText("resText", res);
});