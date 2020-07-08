
<div id="sideNav">
        <nav class="nav">
            <div class ="myTocHeader">
                <a class="nav-link" href="#"> Machine Motion </a>
            </div>
           
            % for function in functions:
            <div class = "myTocItem">
                <a href="#${function.name}">${function.name}</a>
            </div>
            % endfor
        
        </nav>

</div>
