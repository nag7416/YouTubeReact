const profilebtn = document.getElementById('profilebtn');
const profilecard = document.getElementById('profilecard');

profilebtn.addEventListener('click', () => {
	profilecard.classList.toggle('active');
})




var menubtn = document.querySelector('.left .menu button');
var side = document.querySelector('.main .side');

menubtn.addEventListener('click', function(){
	side.classList.toggle('active');
})