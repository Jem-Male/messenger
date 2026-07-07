// 1. Находим нашу форму в HTML по её ID
const loginForm = document.getElementById('loginForm');
const errorText = document.getElementById('errorText');

// 2. Вешаем "слушателя событий". Когда форма будет отправлена ('submit'), запустится эта функция.
loginForm.addEventListener('submit', async (event) => {
    
    // ВАЖНО: По умолчанию при отправке формы браузер перезагружает страницу.
    // Нам это не нужно, мы хотим отправить данные скрыто (через fetch).
    // preventDefault() отменяет стандартное поведение браузера.
    event.preventDefault(); 

    // Очищаем прошлые ошибки
    errorText.textContent = "";

    // 3. Достаем значения, которые юзер ввел в поля
    const emailValue = document.getElementById('email').value;
    const passwordValue = document.getElementById('password').value;

    try {
        // 4. Отправляем POST запрос на наш FastAPI
        const response = await fetch("http://127.0.0.1:8000/login", {
            method: "POST", // Указываем метод
            headers: {
                // Говорим серверу, что отправляем данные в формате JSON
                "Content-Type": "application/json" 
            },
            // Превращаем JS-объект в строку JSON (как того требует Pydantic)
            body: JSON.stringify({
                email: emailValue,
                password: passwordValue
            })
        });

        // 5. Ждем, пока сервер ответит, и переводим ответ из JSON в JS-объект
        const data = await response.json();

        // 6. Проверяем, успешный ли ответ
        if (response.ok) {
            // Если всё ок (сервер выдал 200 и поставил куку)
            alert("Вы успешно вошли!");
            // Позже здесь мы напишем код для перехода на страницу чата
            // window.location.href = "chat.html"; 
        } else {
            // Если сервер выдал ошибку (например, 400 Bad Request),
            // мы берем текст ошибки из FastAPI (data.detail) и выводим на экран
            errorText.textContent = data.detail;
        }

    } catch (error) {
        // Если сервер вообще не ответил (выключен)
        errorText.textContent = "Ошибка соединения с сервером";
    }
});