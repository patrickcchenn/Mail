document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');




  // Send mail button
  document.querySelector('#compose-form').onsubmit = function () {
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
      })
    })
      .then(response => response.json())
      .then(result => {
        // Print result
        console.log(result);
        load_mailbox('sent');

      });
  }



});





function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  //show all of the letters
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
      // Print emails
      console.log(emails);

      // ... do something else with emails ...
      emails.forEach(mail => {
        let element = document.createElement('div');
        if (mail['read'] == true) {
          element.innerHTML = `<div style='border-style:groove ;background-color: grey'><b>${mail["recipients"]}</b> ${mail["subject"]} <p style='text-align: right'>${mail["timestamp"]}</p> </div>`;
        }
        else {
          element.innerHTML = `<div style='border-style:groove '><b>${mail["recipients"]}</b> ${mail["subject"]} <p style='text-align: right'>${mail["timestamp"]}</p> </div>`;
        }
        element.addEventListener('click', function () {
          console.log('This elemensdt has been clicked!')
          fetch(`/emails/${mail['id']}`, {
            method: 'PUT',
            body: JSON.stringify({
              read: true
            })
          })
          show_mail(mail, mailbox)
        });
        document.querySelector('#emails-view').append(element);
      });
    });

}

function show_mail(mail, mailbox) {
  document.querySelector('#emails-view').innerHTML = ''
  fetch(`/emails/${mail['id']}`)
    .then(response => response.json())
    .then(email => {
      // Print email
      console.log(email);

      // ... ADD ELEMENT INTO DIV
      // Reply and archive button
      let element = document.createElement('div');
      if (mailbox == 'sent') {
        element.innerHTML = `From: ${email['sender']}<br>To: ${email['recipients']}<br>Subject: ${email['subject']}<br>Timestamp: ${email['timestamp']}<br>`
        element.innerHTML += `<button class="btn btn-sm btn-outline-primary" id='reply' >Reply</button> <button class="btn btn-sm btn-outline-primary" id='archive' style='display: none;' >Unarchive</button> <hr>`
      }
      else {
        element.innerHTML = `From: ${email['sender']}<br>To: ${email['recipients']}<br>Subject: ${email['subject']}<br>Timestamp: ${email['timestamp']}<br>`
        if (mailbox == 'archive') {
          element.innerHTML += `<button class="btn btn-sm btn-outline-primary" id='reply' >Reply</button> <button class="btn btn-sm btn-outline-primary" id='archive' >Unarchive</button><hr>`
        }
        else {
          element.innerHTML += `<button class="btn btn-sm btn-outline-primary" id='reply' >Reply</button> <button class="btn btn-sm btn-outline-primary" id='archive' >Archive</button><hr>`
        }
      }


      document.querySelector('#emails-view').append(element);
      document.querySelector('#reply').addEventListener('click', () => reply_email(email, mailbox));

      //FIX RE: RE: AND I THINK THIS PROJECT IS DONE
      document.querySelector('#archive').onclick = () => {
        if (mailbox == 'archive') {
          fetch(`/emails/${email['id']}`, {
            method: 'PUT',
            body: JSON.stringify({
              archived: false
            })
          })
        }
        else {
          fetch(`/emails/${email['id']}`, {
            method: 'PUT',
            body: JSON.stringify({
              archived: true
            })
          })
          console.log("aaaaaaa");

        }

        load_mailbox('inbox')
      }

      let body = document.createElement('div')
      body.innerHTML = `${email['body']}`
      document.querySelector('#emails-view').append(body);
      // document.querySelector('#email-view').style.display = 'block';


    });


}

function reply_email(email, mailbox) {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // PRE FILL FIELDS
  if (mailbox == 'sent') {
    document.querySelector('#compose-recipients').value = email['recipients'];
  }
  else {
    document.querySelector('#compose-recipients').value = email['sender'];
  }
  if (email['subject'].includes('Re:')) {
    document.querySelector('#compose-subject').value = `${email['subject']}`;
  }
  else {
    document.querySelector('#compose-subject').value = `Re: ${email['subject']}`;
  }

  document.querySelector('#compose-body').value = `On ${email['timestamp']} ${email['sender']} wrote: ${email['body']} <br>`;
}
