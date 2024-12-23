function searchFunction() {
    const input = document.getElementById('search').value.toLowerCase();
    const people = document.querySelectorAll('.card');
    const quotes = document.querySelectorAll('.quotes_card');

    // Фильтрация людей
    people.forEach(person => {
        const name = person.textContent.toLowerCase();
        person.style.display = name.includes(input) ? '' : 'none';
    });

    // Фильтрация цитат
    quotes.forEach(quote => {
        const text = quote.textContent.toLowerCase();
        quote.style.display = text.includes(input) ? '' : 'none';
    });
}