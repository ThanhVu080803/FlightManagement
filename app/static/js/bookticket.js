let bookTicketBtn = document.querySelector('.book-ticket-btn')

bookTicketBtn.addEventListener('click', e => {
    let departure_id = document.querySelector('select#departure').value
    let destination_id = document.querySelector('select#destination').value
    let departure_time = new Date(document.querySelector('#departure-date').value)
    let currentDate = new Date()

    if(departure_id === destination_id){
        alert('Chọn điểm đến và điểm đi không hợp lệ!!!')
        e.preventDefault()
    } else if(departure_time < currentDate){
        alert('Chọn ngày đi không hợp lệ!!!')
        e.preventDefault()
    }
})