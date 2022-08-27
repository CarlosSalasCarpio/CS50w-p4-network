function like_post(post_number, user_id) {

  fetch('/like_post_api/' + post_number)
  .then(response => response.json())
  .then(post => {
    document.querySelector('#post_' + post_number).innerHTML = post.likes_number;

    likes = post.liked_by

    console.log(likes, parseInt(user_id));

    if (likes.includes(parseInt(user_id))) {
      document.querySelector('#like_button_' + post_number).src = "/static/network/unlike.png";
      console.log('liked')
    }
    else {
      document.querySelector('#like_button_' + post_number).src = "/static/network/like.png";
      console.log('not')
    }
  });

  

  return false
}


function edit_post(post_number) {

  let edit_textarea = document.querySelector('#edit_textarea_' + post_number); 
  let edit_button = document.querySelector('#edit_button_' + post_number);
  let post_body = document.querySelector('#post_body_' + post_number);

  if (edit_textarea.style.display === 'none') {
    edit_textarea.style.display = 'block';
    edit_button.style.display = 'block';
    post_body.style.display = 'none';

    edit_button.addEventListener('click', () => save_post(post_number));

  } else {
    edit_textarea.style.display = 'none';
    edit_button.style.display = 'none';
    post_body.style.display = 'block';
  }

  
}


function save_post(post_number) {
  let textarea = document.querySelector('#edit_textarea_' + post_number).value

  fetch('/edit_post_api/' + post_number + '/' + textarea)
  .then(response => response.json())
  .then(post => {
    console.log(post)
    document.querySelector('#post_body_' + post_number).innerHTML = textarea;

    let edit_textarea = document.querySelector('#edit_textarea_' + post_number);
    let edit_button = document.querySelector('#edit_button_' + post_number);
    let post_body = document.querySelector('#post_body_' + post_number);

    edit_textarea.style.display = 'none';
    edit_button.style.display = 'none';
    post_body.style.display = 'block';
  });
}