function posting() {
    post = document.getElementById("submit_button");
    alias = document.getElementById("alias_form");
    content_form = document.getElementById("content_form");
    alias_check = document.getElementById("alias_check");
    content_check = document.getElementById("content_check");

    document.getElementById("alias_length").innerHTML = "Characters: " + alias.value.length + " | Min: 2 | Max: 15";
    document.getElementById("content_length").innerHTML = "Characters: " + content_form.value.length + " | Min: 10 | Max: 150";
     

    if (alias.value.length > 1 && alias.value.length < 16) { //When the Alias has more than 1 character
        alias_check.style.color = "lightgreen";
        alias_status = true;
    }
    else {
        alias_check.style.color = "lightgrey";
        alias_status = false;
    }
    
    if (content_form.value.length > 9 && content_form.value.length < 151) {
        content_check.style.color = "lightgreen";
        content_status = true;
    }
    else {
        content_check.style.color = "lightgrey";
        content_status = false;
    }

    if (alias_status == true && content_status == true) {
        post.disabled = false;
    }
    else{
        post.disabled = true;
    }
}
