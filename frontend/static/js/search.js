function searchFunction() {
    const input = document.getElementById('search').value.toLowerCase();
    const people = document.querySelectorAll('.people');
    const cards = document.querySelectorAll('.card');
    const quotes = document.querySelectorAll('.quotes');
    const quotesCards = document.querySelectorAll('.quotes_card');

    // Фильтрация людей
    people.forEach((person, index) => {
        const name = person.textContent.toLowerCase();
        const card = cards[index];
        card.style.display = name.includes(input) || input === '' ? '' : 'none';
    });

    // Фильтрация цитат
    quotes.forEach((quote, index) => {
        const text = quote.textContent.toLowerCase();
        const quoteCard = quotesCards[index];
        quoteCard.style.display = text.includes(input) || input === '' ? '' : 'none';
    });
}
