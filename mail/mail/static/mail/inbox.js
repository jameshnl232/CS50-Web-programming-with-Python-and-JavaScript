document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  
  // By default, load the inbox
  load_mailbox('inbox');

  document.querySelector('#compose-form').addEventListener('submit', send_email);
});

function send_email(event) {
  event.preventDefault(); // Prevent the default form submission

  const recipients = document.querySelector('#compose-recipients').value;
  const compose_subject = document.querySelector('#compose-subject').value;
  const compose_body = document.querySelector('#compose-body').value;
  
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: compose_subject,
        body: compose_body 
  })
  });
  
  load_mailbox('sent');

  return false;

}


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#single-email-view').style.display = 'none';



  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}



function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';


  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  function view_email(email){

    const emailDiv = document.createElement('div');
    emailDiv.classList.add('email-box'); // Add a CSS class for styling
    if(email.read === true){
      emailDiv.style.color = 'gray';
    }

    emailDiv.innerHTML = `
      <div class="${email.read?'read':'unread'} row m-1">
                <div class="col-sm-3 email-sender"><strong>${email.sender}</strong></div>
                <div class="col-sm-6 email-title">${email.subject}</div>
                <div class="col-sm-3 email-date">${email.timestamp}</div>
      </div>
    `;

    // Append the container div to the emails view
    document.querySelector('#emails-view').appendChild(emailDiv);

    //when clicking on an email
    emailDiv.addEventListener('click', (event) => {
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#single-email-view').style.display = 'block';
      
      fetch(`/emails/${email.id}`)
      .then(response => response.json())
      .then(email => { 

        fetch(`/emails/${email.id}`, {
          method: 'PUT',
          body: JSON.stringify({
              read: true
          })
        });

        document.querySelector('#single-email-from').innerHTML = email.sender;
        document.querySelector('#single-email-to').innerHTML = email.recipients;
        document.querySelector('#single-email-subject').innerHTML = email.subject;
        document.querySelector('#single-email-timestamp').innerHTML = email.timestamp;
        document.querySelector('#single-email-content').innerHTML = email.body;


        if(email.archived != true){
          document.querySelector('#unarchive-button').style.display = 'none';
          document.querySelector('#archive-button').style.display = 'inline';
          document.querySelector('#archive-button').onclick = () => {
            fetch(`/emails/${email.id}`, {
              method: 'PUT',
              body: JSON.stringify({
                  archived: true
              })
            })
            load_mailbox('inbox');
          };
        }
        else{
          document.querySelector('#archive-button').style.display = 'none';
          document.querySelector('#unarchive-button').style.display = 'inline';
          document.querySelector('#unarchive-button').onclick = () => {
            fetch(`/emails/${email.id}`, {
              method: 'PUT',
              body: JSON.stringify({
                  archived: false
              })
            })
            load_mailbox('inbox');
          };
        }
        if(mailbox === 'sent'){
          document.querySelector('#archive-button').style.display = 'none';
          document.querySelector('#unarchive-button').style.display = 'none';
        }

        document.querySelector('#reply-button').onclick = () => {
          document.querySelector('#single-email-view').style.display = 'none';
          document.querySelector('#compose-view').style.display = 'block';
          document.querySelector('#compose-from').style.display = 'none';

          document.querySelector('.compose-heading').innerHTML = "Reply";
          document.querySelector('#compose-recipients').value = `${email.sender}`;
          let compose_input = document.querySelector('#compose-subject');
          if(!email.subject.toUpperCase().startsWith("RE")){
            compose_input.value = `Re: ${email.subject}`;
          }
          else{
            compose_input.value = email.subject;
          }
          document.querySelector('#last-message').innerHTML = `On Jan 1 2020, 12:00 AM ${email.sender} wrote: ${email.body}`;
        }

        


    });


    }); //end email clicking

    if(mailbox === 'sent'){
      emailDiv.style.color = 'gray';
    }
    

  } //End view_mail

  if(mailbox === 'sent'){
      fetch('/emails/sent')
      .then(response => response.json())
      .then(emails => {
        emails.forEach(email => view_email(email));
      });
  } 

  if (mailbox === 'inbox') {
    fetch('/emails/inbox')
        .then(response => response.json())
        .then(emails => {
            emails.forEach(email => {
                view_email(email);
            });
        });
}

if(mailbox === 'archive'){
  fetch('/emails/archive')
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => view_email(email));

  });
}


}

