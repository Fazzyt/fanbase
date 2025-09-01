function searchFunction() {
    const input = document.getElementById('search');
    if (!input) return;
    const filter = input.value.trim().toLowerCase();

    // Фильтрация карточек людей (index.html)
    document.querySelectorAll('.people').forEach(person => {
        const card = person.closest('.card');
        if (!card) return;
        const name = person.textContent.trim().toLowerCase();
        card.style.display = (filter === '' || name.includes(filter)) ? '' : 'none';
    });

    // Фильтрация карточек цитат (person.html)
    document.querySelectorAll('.quotes').forEach(quote => {
        const quoteCard = quote.closest('.quotes_card');
        if (!quoteCard) return;
        const text = quote.textContent.trim().toLowerCase();
        quoteCard.style.display = (filter === '' || text.includes(filter)) ? '' : 'none';
    });
}
