
<div class="row">



    <div class="col-md-10 col-sm-12" id="machine-motion-content">
        <img  style="width:90%" src= "https://s3.amazonaws.com/ventioncms/vention_images/images/000/002/182/large/api-reference.jpg?1573771416">
        ${apiIntro}
        
        ${content}
    </div>




</div>


        
<style>
    ${cssNative}
</style>
<style>
    ${cssStyles}
</style>
<script>
    $( document ).ready(function() {

 
        var title = document.getElementsByClassName("technical-document-title")[0].parentNode
        var content = document.getElementById("machine-motion-content")
        content.insertBefore(title, content.childNodes[0])

        var sideNav = document.getElementById('sideNav')



        $(window).scroll(function(){ // scroll event
            var windowTop = $(window).scrollTop(); // returns number
        
            if(windowTop > 200 - 90){
                sideNav.classList.add("sticky-side-nav");
               

            } else {
                sideNav.classList.remove("sticky-side-nav");
              }

        });
    });

    function copyTextToClipboard(id, funcName) {

        var copyText = document.getElementById(id).innerText
        console.log(copyText)
        var dummy = document.createElement("textarea");

        document.body.appendChild(dummy);
       
        dummy.value = copyText;
        dummy.select();
        document.execCommand("copy");
        document.body.removeChild(dummy);

        alert("Code Copied To Clipboard")

    }


</script>
