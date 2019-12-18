class Utility {
  constructor() {}

  static clearView() {
    // called on each hash change to hide the previous view boxes
    let toHide = document.getElementsByClassName('hideable');
    for (let i = 0; i < toHide.length; i++) {
      toHide[i].style.display = 'none';
    }
  }
  static showLoggedInHeader() {
    // change to the header for authenticated users
    document.getElementById('not-auth-header').style.display = 'none';
    document.getElementById('auth-header').style.display = 'block';
  }
  static showLoggedOutHeader() {
    // change to the header for authenticated users
    document.getElementById('not-auth-header').style.display = 'block';
    document.getElementById('auth-header').style.display = 'none';
  }
  static hideMessage() {
    let box = document.getElementById('message-box');
    box.style.display = 'none';
  }
  static displayMessage(message) {
    let box = document.getElementById('message-box');
    let messageText = document.getElementById('message');
    messageText.innerHTML = message;
    box.style.display = 'block';
    window.setTimeout(this.hideMessage, 3000);
  }
  static load(templateId, containerId, authenticated) {
    // loads (shows) the template and also clears the data container (if provided)
    let template = document.getElementById(templateId);
    template.style.display = 'block';
    if (containerId) {
      let container = document.getElementById(containerId);
      container.innerHTML = '';
    }
    if (authenticated) {
      this.showLoggedInHeader();
    }
    else {
      this.showLoggedOutHeader();
    }
  }
  static formData(formId) {
    // gets data from an HTML form
    let form = document.getElementById(formId);
    let formData = new FormData(form);
    form.reset();
    return formData;
  }
  static async submit(url, requestBody) {
    let request = new Request(url);
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const headers = new Headers({
      'Content-Type': 'application/json', 'X-CSRFToken': csrftoken});
    let init = {'method': 'POST', 'body': JSON.stringify(requestBody), 
      'credentials': 'include', 'headers': headers};
    let response = await fetch(request, init);
    let message = '';
    let fail = false;
    if (!response.ok) {
      message = 'HTTP Error, Status: ' + response.status + '<br>';
      fail = true;
    }
    let responseData = await response.json();
    if (!responseData.success) {
      message += responseData.errors.join('\n');
      fail = true;
    }
    if (fail) {
      this.displayMessage(message);
      return false;
    }
    else {
      return responseData;
    }
  }
  static changeHash(event) {
    event.preventDefault();
    event.stopPropagation();
    let hash = '/';
    if (event.currentTarget.href) {
      let fullUrl = event.currentTarget.href;
      hash = fullUrl.slice(fullUrl.indexOf('#'));
    }
    else if (event.currentTarget.parentElement.action) {
      let fullUrl = event.currentTarget.parentElement.action;
      hash = fullUrl.slice(fullUrl.indexOf('#'));
    }
    window.location.hash = hash;
  }
}