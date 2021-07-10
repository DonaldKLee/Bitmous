window.onload = function() { //Runs posting again if user form does not submit. This makes it so that the green checkmarks validate again
  posting();
  tag_added();
};


function posting() {
    post = document.getElementById("submit_button");
    alias = document.getElementById("alias_form");
    content_form = document.getElementById("content_form");
    alias_check = document.getElementById("alias_check");
    content_check = document.getElementById("content_check");

    document.getElementById("alias_length").innerHTML = "Characters: " + alias.value.trim().length + " | Min: 2 | Max: 15";
    document.getElementById("content_length").innerHTML = "Characters: " + content_form.value.trim().length + " | Min: 10 | Max: 150";
     

    if (alias.value.trim().length > 1 && alias.value.trim().length < 16) { //When the Alias has more than 1 character
        alias_check.style.color = "lightgreen";
        alias_status = true;
    }
    else {
        alias_check.style.color = "lightgrey";
        alias_status = false;
    }
    
    if (content_form.value.trim().length > 9 && content_form.value.trim().length < 151) {
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

function tag_added() {
    real_tags_form = document.getElementById("all_tags");
    var list_tags = real_tags_form.value.split(" ")
    var tags = []
    for (i=0; i < list_tags.length; i++) {
        if (list_tags[i]) {
            tags.push(list_tags[i])
        }
    }
    // Removes all tags
    var displayed_tags = document.getElementById("the_tags");
    for (tag = 0; tag < displayed_tags.childNodes.length; tag++) {
        tag = -1 // The list decreases everytime it runs, so only half the loop is ran, this prevents that from happening
        displayed_tags.removeChild(displayed_tags.childNodes[0]);
    }
    // Adds all tags
    if (tags.length) {
        for (i=0; i < tags.length; i++) {
            tags_container = document.getElementById("the_tags");
            tags_container.innerHTML += '<button class="display_tag_box" type="button" onclick=removetag("' + tags[i] + '")>#' + tags[i] + ' <i class="tag_delete fas fa-times"></i></button>';
            
        }
    }
}

function removetag(the_tag) {
    tags_form = document.getElementById("all_tags");
    tags_form.value = tags_form.value.replace(the_tag, "").trim();

    tag_added()
}

function adding_tags() {
    real_tags_form = document.getElementById("all_tags");
    var tags = real_tags_form.value.split(" ")
    tags = tags.filter(item => item);
    tags_form = document.getElementById("make_tag");
    tags_form.value = tags_form.value.replace(/[^\w\s]/gi, ''); // Removes symbols from input box

    if (tags_form.value.indexOf(' ') >= 0) {
        console.log(tags);
        if (tags.includes(tags_form.value.replace(/\s/g, ''))) {
            console.log("Already in!")
            tags_form.value = ""
        }
        else if (tags.length < 5) {
            tags_form.value = tags_form.value
            real_tags_form.value += " " + tags_form.value
            real_tags_form.value = real_tags_form.value.toLowerCase().replace(/\s\s+/g, ' ').trim()
            tags_form.value = ""
        }
        else {
            tags_form.value = tags_form.value.replace(/\s/g, '')
            console.log("You can't add anymore tags!");
        }
        tag_added()
    }
}