document.addEventListener('DOMContentLoaded', function() {
    load_page('all-posts');

    if(document.querySelector('#new-post-form')){
        document.querySelector('#new-post-form').addEventListener('submit', create_new_post);
    }



    //create new post
    function create_new_post(event){
        //event.preventDefault(); // Prevent the default form submission
        const content = document.querySelector('#new-post-content').value;

        fetch('/new-post', {
            method: 'POST',
            body: JSON.stringify({
                content: content
            })
        });

        return false; 
    }


    //load all posts
    function load_page(page){
        if(page != "all-posts"){
            document.querySelector('#new-post').style.display = 'none';
        }
    }




    const posts = document.querySelectorAll('.post-div');

    posts.forEach(post => {
        const heart = post.querySelector(".heart");
        const liked = post.querySelector("input.liked");
        const logged_in = post.querySelector("input.logged-in").value;
        const post_id = post.querySelector("input.post-id").value;
        const post_content_div = post.querySelector("div.post-content");
        const original_html = post_content_div.innerHTML;
        const original_text = post_content_div.textContent;
        const edit_div = post.querySelector("span.edit-post");
        const like_label = post.querySelector("span.like-label");
        const like_count = post.querySelector("span.like-count");

        if(liked){
            like_label.classList.add("liked-post");
            heart.style.color = "red";
        }
        else{
            like_label.classList.remove("liked-post");

        }

        function restoreView(text){
            post_content_div.innerHTML = original_html;
            post_content_div.textContent = text;
            edit_div.style.display = 'block';
        }

        if(edit_div){
            edit_div.addEventListener("click", function(){
                edit_div.style.display = 'none';

                post_content_div.innerHTML = `
                <div class="container">
                    <div class="row">
                        <div class="col">
                            <textarea autofocus type="text" class=" form-control my-2 edit-textarea">${original_text.trim()}</textarea>
                        </div>
                    </div>
                    <div class="row">
                        <button type="button" class="mx-1 save-post col- btn btn-primary">Save</button>
                        <span><button type="button" class="mx-1 cancel-post col btn btn-primary">Cancel </button></span>
                    </div>
                </div>

                `;

                const save_button = post_content_div.querySelector(".save-post");
                save_button.addEventListener("click", () => {
                    //fetch and put 
                    const new_text = post_content_div.querySelector(".edit-textarea").value;
                    fetch(`/posts/${post_id}`, {
                        method: "PUT",
                        body: JSON.stringify({
                            content: new_text
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if(data["edited"]){
                            restoreView(new_text);
                        }
                        else{
                            restoreView(original_text);
                        }
                    })

                });


                const cancel_button = post_content_div.querySelector(".cancel-post");
                cancel_button.addEventListener("click", () => {
                    post_content_div.innerHTML = original_html;
                    edit_div.style.display = 'block';

                });
            });
        }



        //handling liking feature 
        like_label.addEventListener("click", function(){
            if(logged_in === "True"){
                fetch(`/toggle_like/${post_id}/`, {
                    method: "POST",
                    body: JSON.stringify({
                        //nothing
                    })
                })
                .then(response => response.json())
                .then(data => {

                    like_switch(data["like_count"], data["like_status"]);
                })
                .catch(error => {
                    console.error("Error:", error);
                    // Handle error if necessary
                });
            }
            else{
                alert("Not logged in!");
            }
        
        });

        function like_switch(like_number, like_status){
            like_count.textContent = like_number;
            if(like_status){
                like_label.classList.add("liked-post");
                heart.style.color = "red";

            }
            else{
                like_label.classList.remove("liked-post") 
                heart.style.color = "";

            }
        }
         
        
    });


    



});