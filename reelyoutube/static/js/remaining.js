

    var channelbtn = document.querySelector('#channelbtn');
    var overlaybox = document.querySelector('.overlay');
    var imgpreview = document.querySelector('.img-preview');
    var filebtn = document.getElementById('filebtn');
    var cancelbtn = document.querySelector('.uploadbox .bottom a');
    var createchannelbtn = document.querySelector('.uploadbox .bottom button');
    var channelsuccessoverlay = document.querySelector('.overlay .create');
    var channelcreateform = document.getElementById('channelcreateform');

    if(filebtn){
        filebtn.addEventListener('change', function(e){
            var file = filebtn.files[0];
            var url = URL.createObjectURL(file);
            var img = document.createElement('img');
            imgpreview.innerHTML = `<img src=${url}>`;
        })
    }
    if(cancelbtn){
        cancelbtn.addEventListener('click', () => {
            overlaybox.classList.toggle('active');
            channelcreateform.clear();
        })
    }
    
    if(channelbtn){
        channelbtn.addEventListener('click', function(){
            channelbtn.classList.toggle('active');
            overlaybox.classList.toggle('active');
        })
    }
    
    if(createchannelbtn){
        createchannelbtn.addEventListener('click', function(){
            channelsuccessoverlay.classList.toggle('active');
    
            setTimeout(() => {
                channelsuccessoverlay.classList.toggle('active');
                overlaybox.classList.toggle('active');
            }, 2000);
        })
    }

    var user = "{{request.user.id}}";
    var id_channeluser = document.getElementById('id_channeluser');
    if(user && id_channeluser){
        id_channeluser.value = user;
    }

    channelcreateform.addEventListener('submit', function(e){
        e.preventDefault();

        var id = channelcreateform.querySelector('#id_id');
        var channelname = channelcreateform.querySelector('#id_channelname');
        var channeluser = channelcreateform.querySelector('#id_channeluser').value;
        var channelimg = channelcreateform.querySelector('#filebtn').files[0];
        //var banner = channelcreateform.querySelector('#id_banner').files[0];
        var url = channelcreateform.getAttribute('action');
        var csrf = document.getElementsByName('csrfmiddlewaretoken');

        var fd = new FormData();
        fd.append('id', id.value);
        fd.append('channelname', channelname.value);
        fd.append('channeluser', channeluser);
        fd.append('channelimg', channelimg);
        //fd.append('banner', banner);
        fd.append('csrfmiddlewaretoken', csrf[0].value);

        $.ajax({
            type: 'POST',
            url: url,
            data: fd,
            success: function(res){
                console.log(res);
                setTimeout(function(){
                    window.location.href = 'channel/'+id.value;
                }, 2500)
            },
            error: function(err){
                console.log(err);
            },
            contentType: false,
            processData: false,
            cache: false,
        })
    })


    function subscribe(element) {
        let name = element.dataset.channelslug;

        console.log(name);

        fetch(name +'/subscribe', {
            method: 'PUT',
        })
        .then((res) => {
            let label = element.parentElement.parentElement.querySelector('.channel-name label span');
            var count = label.innerHTML;
            count++;
            label.innerHTML = count;
            element.setAttribute('id', 'subscribed');
            element.innerHTML = 'Subscribed';
            element.insertAdjacentHTML('afterend', '<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" class="style-scope yt-icon" style="pointer-events: none;"><g class="style-scope yt-icon"><path d="M10,20h4c0,1.1-0.9,2-2,2S10,21.1,10,20z M20,17.35V19H4v-1.65l2-1.88v-5.15c0-2.92,1.56-5.22,4-5.98V3.96 c0-1.42,1.49-2.5,2.99-1.76C13.64,2.52,14,3.23,14,3.96l0,0.39c2.44,0.75,4,3.06,4,5.98v5.15L20,17.35z M19,17.77l-2-1.88v-5.47 c0-2.47-1.19-4.36-3.13-5.1c-1.26-0.53-2.64-0.5-3.84,0.03C8.15,6.11,7,7.99,7,10.42v5.47l-2,1.88V18h14V17.77z" class="style-scope yt-icon"></path></g></svg>');
            element.setAttribute('onclick', 'unsubscribe(this)');
        })
        .catch(error => {
            if(error.status >= 400){
                console.log("error");
            }
        })
    }
    function unsubscribe(element) {
        let name = element.dataset.channelslug;

        fetch(name+'/unsubscribe', {
            method: 'PUT',
        })
        .then((res) => {
            
            let label = element.parentElement.parentElement.querySelector('.channel-name label span');
            var count = label.innerHTML;
            count--;
            label.innerHTML = count;
            element.removeAttribute('id', 'subscribed');
            element.innerHTML = 'Subscribe';
            var h1 = element.parentElement.querySelector('svg');
            var parent = element.parentElement;
            parent.removeChild(h1);
            element.setAttribute('onclick', 'subscribe(this)');
        })
        .catch(error => {
            if(error.status >= 400){
                console.log("error");
            }
        })
    }

    function like_video(element){
        var id = element.dataset.video_id;

        fetch(id+'/like', {
            method: 'PUT',
        })
        .then(res => {
            var count = element.querySelector('label');
            var value = count.innerHTML;
            value++;
            count.innerHTML = value;
            element.querySelector('svg').innerHTML = `<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" class="style-scope yt-icon" style="pointer-events: none;"><g class="style-scope yt-icon"><path d="M3,11h3v10H3V11z M18.77,11h-4.23l1.52-4.94C16.38,5.03,15.54,4,14.38,4c-0.58,0-1.14,0.24-1.52,0.65L7,11v10h10.43 c1.06,0,1.98-0.67,2.19-1.61l1.34-6C21.23,12.15,20.18,11,18.77,11z" class="style-scope yt-icon"></path></g></svg>`;
            element.setAttribute('onclick', 'unlike_video(this)');
        })
    }
    function unlike_video(element){
        var id = element.dataset.video_id;

        fetch(id+'/unlike', {
            method: 'PUT',
        })
        .then(res => {
            var count = element.querySelector('label');
            var value = count.innerHTML;
            value--;
            count.innerHTML = value;
            element.querySelector('svg').innerHTML = `<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" class="style-scope yt-icon" style="pointer-events: none;"><g class="style-scope yt-icon"><path d="M18.77,11h-4.23l1.52-4.94C16.38,5.03,15.54,4,14.38,4c-0.58,0-1.14,0.24-1.52,0.65L7,11H3v10h4h1h9.43 c1.06,0,1.98-0.67,2.19-1.61l1.34-6C21.23,12.15,20.18,11,18.77,11z M7,20H4v-8h3V20z M19.98,13.17l-1.34,6 C18.54,19.65,18.03,20,17.43,20H8v-8.61l5.6-6.06C13.79,5.12,14.08,5,14.38,5c0.26,0,0.5,0.11,0.63,0.3 c0.07,0.1,0.15,0.26,0.09,0.47l-1.52,4.94L13.18,12h1.35h4.23c0.41,0,0.8,0.17,1.03,0.46C19.92,12.61,20.05,12.86,19.98,13.17z" class="style-scope yt-icon"></path></g></svg>`;
            element.setAttribute('onclick', 'like_video(this)');
        })
    }

    function some(){
        var video = document.querySelectorAll('#videourl video');
        for(let i=0; i<video.length; i++){
            video[i].style.display = 'none';
            video[i].onloadedmetadata = function(){ 
                var hours = parseInt(this.duration / 3600);
                var minutes = parseInt((this.duration % 3600) / 60);
                var seconds = parseInt((this.duration % 3600) % 60);
                if(seconds < 10){
                    seconds = "0"+seconds;
                }
                if(minutes < 10 && minutes != 0){
                    minutes = "0"+minutes;
                } else if(minutes < 10 && minutes == 0) 
                {
                    minutes = minutes;
                }
                if (hours<=0){
                    this.parentElement.querySelector('p').innerHTML = minutes+":"+seconds;
                } else {
                    this.parentElement.querySelector('p').innerHTML = hours+":"+minutes+":"+seconds;
                }
            }
        }
        for(let i=0; i<video.length; i++){
            video[i].addEventListener('ended', function(){
                console.log('ended');
            })
        }
    }
    some();

    var notificationbtn = document.getElementById('notification');
    var notifbox = document.querySelector('.notificationbox');
    
    notificationbtn.addEventListener('click', function(){
        notifbox.classList.toggle('active');
    })


    var micbtn = document.getElementById('mic');
    var input = document.querySelector('.search input');
    var searchbtn = document.querySelector('.search #search');
    
    micbtn.addEventListener('click', function(){
        var speech = true;
        window.SpeechRecognition = window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.interimResults = true;
    
        recognition.addEventListener('result', e => {
            const transcript = Array.from(e.results)
            .map(result => result[0])
            .map(result => result.transcript)
    
            input.value = transcript;
            console.log(transcript);
        })
    
        if(speech == true){
            recognition.start();
        }
        recognition.onspeechend = function() {
            setTimeout(() => {
                searchbtn.click();
            }, 1000)
        }
    })
    

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

function likecomment(element){
    let video_id = element.parentElement.parentElement.parentElement.dataset.video;
    let comment_id = element.parentElement.parentElement.parentElement.dataset.comment;
    
    fetch(video_id+'/'+comment_id+'/like', {
        method: 'PUT',
    })
    .then((res) => {
        var svg = `<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" class="style-scope yt-icon" style="pointer-events: none;"><g class="style-scope yt-icon"><path d="M3,11h3v10H3V11z M18.77,11h-4.23l1.52-4.94C16.38,5.03,15.54,4,14.38,4c-0.58,0-1.14,0.24-1.52,0.65L7,11v10h10.43 c1.06,0,1.98-0.67,2.19-1.61l1.34-6C21.23,12.15,20.18,11,18.77,11z" class="style-scope yt-icon"></path></g></svg>`;
        var count = element.querySelector('label');
        var value = count.innerHTML;
        value++;
        count.innerHTML = value;
        element.innerHTML = svg + `<label>${value}</label>`;
        element.setAttribute('onclick', 'unlikecomment(this)');
    })
    .catch((error) => {
        console.log(error);
    })
}
function unlikecomment(element){
    let video_id = element.parentElement.parentElement.parentElement.dataset.video;
    let comment_id = element.parentElement.parentElement.parentElement.dataset.comment;
    
    fetch(video_id+'/'+comment_id+'/unlike', {
        method: 'PUT',
    })
    .then((res) => {
        var svg = `<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" class="style-scope yt-icon" style="pointer-events: none;"><g class="style-scope yt-icon"><path d="M18.77,11h-4.23l1.52-4.94C16.38,5.03,15.54,4,14.38,4c-0.58,0-1.14,0.24-1.52,0.65L7,11H3v10h4h1h9.43 c1.06,0,1.98-0.67,2.19-1.61l1.34-6C21.23,12.15,20.18,11,18.77,11z M7,20H4v-8h3V20z M19.98,13.17l-1.34,6 C18.54,19.65,18.03,20,17.43,20H8v-8.61l5.6-6.06C13.79,5.12,14.08,5,14.38,5c0.26,0,0.5,0.11,0.63,0.3 c0.07,0.1,0.15,0.26,0.09,0.47l-1.52,4.94L13.18,12h1.35h4.23c0.41,0,0.8,0.17,1.03,0.46C19.92,12.61,20.05,12.86,19.98,13.17z" class="style-scope yt-icon"></path></g></svg>`;
        var count = element.querySelector('label');
        var value = count.innerHTML;
        value--;
        count.innerHTML = value;
        element.innerHTML = svg + `<label>${value}</label>`;
        element.setAttribute('onclick', 'likecomment(this)');
    })
    .catch((error) => {
        console.log(error);
    })
}

function deletecommentfun(element){
    var comment_id = element.parentElement.parentElement.parentElement.querySelector('.publicdetail .likescon').dataset.comment;
    var video_id = element.parentElement.parentElement.parentElement.querySelector('.publicdetail .likescon').dataset.video;
    fetch(video_id+"/"+comment_id+'/delete', {
        method: 'PUT',
    })
    .then((res) => {
        var commentlabel = element.parentElement.parentElement.parentElement.parentElement.parentElement.querySelector('.commentcount label span');
        var value = commentlabel.innerHTML;
        value--;
        commentlabel.innerHTML = value;
        var comment = element.parentElement.parentElement.parentElement;
        comment.style.display = 'none';
    })
    .catch((err) => {
        console.log(err);
    })
}

    

    var timeago = document.querySelectorAll('#timeago');
    for(let i=0; i<timeago.length; i++){
        timeago[i].innerHTML = humanized_time_span(timeago[i].innerHTML);
    }