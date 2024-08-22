$(".slider-content").slick({
	centerMode: true,
	centerPadding: "60px",
	slidesToShow: 1,
	autoplay: true,
	autoplaySpeed: 2000,
	prevArrow:
		"<button type='button' class='slick-prev pull-left'><i class='fa fa-angle-left' aria-hidden='true'></i></button>",
	nextArrow:
		"<button type='button' class='slick-next pull-right'><i class='fa fa-angle-right' aria-hidden='true'></i></button>",
});

function quantityTickets(type){
    let quantityInput = document.getElementById('quantity-tickets');
    let currentQuantity = parseInt(quantityInput.value);
    if (type === 'increase') {
        quantityInput.value = currentQuantity + 1;
    } else if ( type === 'decrease' && currentQuantity > 1) {
      quantityInput.value = currentQuantity - 1;
    }
}

function toggleActiveModal(clickedBtn){
    let btns = document.querySelectorAll('.modal-header-btn .nav-item')
    btns.forEach((btn)=>{
        btn.classList.remove('active-modal-header')
    })
    clickedBtn.classList.add('active-modal-header')

    let roundTrip = document.querySelector('.modal-header-btn .nav-item.round-trip')
    document.querySelector('#return-date').disabled = roundTrip.classList.contains('active-modal-header') ? true : false
}