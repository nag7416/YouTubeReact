$(document).ready(function(){
	$('img[src="/static/images/placeholder.jpg"]').each(function(index, el) {
		$(el).attr('src', $(el).data('real-src'));
	});
	$('img[src="/static/images/author.png"]').each(function(index, el) {
		$(el).attr('src', $(el).data('real-src'));
	});
})



const menubtn = document.querySelector('.menu button');
const overlay = document.querySelector('.hiddensidebar');
const hiddenclose = document.getElementById('hiddensidebarclose');
const overlayclose = document.getElementById('closebtn');


menubtn.addEventListener('click', function(){
	overlay.classList.toggle('active');
	hiddenclose.classList.toggle('active');
	overlayclose.classList.toggle('active');
})
hiddenclose.addEventListener('click', function(){
	overlay.classList.toggle('active');
	overlayclose.classList.toggle('active');
	hiddenclose.classList.toggle('active');
})
overlayclose.addEventListener('click', function(){
	overlay.classList.toggle('active');
	overlayclose.classList.toggle('active');
	hiddenclose.classList.toggle('active');
})



const profilebtn = document.getElementById('profilebtn');
const profilecard = document.querySelector('.profilecard');


profilebtn.addEventListener('click', () => {
	profilecard.classList.toggle('active');
})

