
<div class="row">
    <div class="col-md-10 col-sm-12" id="machine-motion-content">
        <img  style="width:90%" src= "https://s3.amazonaws.com/ventioncms/vention_images/images/000/002/182/large/api-reference.jpg?1573771416">      
        ${intro}  
        ${content}
    </div>
</div>

<style>

    .highlight pre { background-color: #404040 }
.highlight .hll { background-color: #404040 }
.highlight .c { color: #999999; font-style: italic } /* Comment */
.highlight .err { color: #a61717; background-color: #e3d2d2 } /* Error */
.highlight .g { color: #d0d0d0 } /* Generic */
.highlight .k { color: #6ab825; font-weight: bold } /* Keyword */
.highlight .l { color: #d0d0d0 } /* Literal */
.highlight .n { color: #d0d0d0 } /* Name */
.highlight .o { color: #d0d0d0 } /* Operator */
.highlight .x { color: #d0d0d0 } /* Other */
.highlight .p { color: #d0d0d0 } /* Punctuation */
.highlight .cm { color: #999999; font-style: italic } /* Comment.Multiline */
.highlight .cp { color: #cd2828; font-weight: bold } /* Comment.Preproc */
.highlight .c1 { color: #999999; font-style: italic } /* Comment.Single */
.highlight .cs { color: #e50808; font-weight: bold; background-color: #520000 } /* Comment.Special */
.highlight .gd { color: #d22323 } /* Generic.Deleted */
.highlight .ge { color: #d0d0d0; font-style: italic } /* Generic.Emph */
.highlight .gr { color: #d22323 } /* Generic.Error */
.highlight .gh { color: #ffffff; font-weight: bold } /* Generic.Heading */
.highlight .gi { color: #589819 } /* Generic.Inserted */
.highlight .go { color: #cccccc } /* Generic.Output */
.highlight .gp { color: #aaaaaa } /* Generic.Prompt */
.highlight .gs { color: #d0d0d0; font-weight: bold } /* Generic.Strong */
.highlight .gu { color: #ffffff; text-decoration: underline } /* Generic.Subheading */
.highlight .gt { color: #d22323 } /* Generic.Traceback */
.highlight .kc { color: #6ab825; font-weight: bold } /* Keyword.Constant */
.highlight .kd { color: #6ab825; font-weight: bold } /* Keyword.Declaration */
.highlight .kn { color: #6ab825; font-weight: bold } /* Keyword.Namespace */
.highlight .kp { color: #6ab825 } /* Keyword.Pseudo */
.highlight .kr { color: #6ab825; font-weight: bold } /* Keyword.Reserved */
.highlight .kt { color: #6ab825; font-weight: bold } /* Keyword.Type */
.highlight .ld { color: #d0d0d0 } /* Literal.Date */
.highlight .m { color: #3677a9 } /* Literal.Number */
.highlight .s { color: #ed9d13 } /* Literal.String */
.highlight .na { color: #bbbbbb } /* Name.Attribute */
.highlight .nb { color: #24909d } /* Name.Builtin */
.highlight .nc { color: #447fcf; text-decoration: underline } /* Name.Class */
.highlight .no { color: #40ffff } /* Name.Constant */
.highlight .nd { color: #ffa500 } /* Name.Decorator */
.highlight .ni { color: #d0d0d0 } /* Name.Entity */
.highlight .ne { color: #bbbbbb } /* Name.Exception */
.highlight .nf { color: #447fcf } /* Name.Function */
.highlight .nl { color: #d0d0d0 } /* Name.Label */
.highlight .nn { color: #447fcf; text-decoration: underline } /* Name.Namespace */
.highlight .nx { color: #d0d0d0 } /* Name.Other */
.highlight .py { color: #d0d0d0 } /* Name.Property */
.highlight .nt { color: #6ab825; font-weight: bold } /* Name.Tag */
.highlight .nv { color: #40ffff } /* Name.Variable */
.highlight .ow { color: #6ab825; font-weight: bold } /* Operator.Word */
.highlight .w { color: #666666 } /* Text.Whitespace */
.highlight .mf { color: #3677a9 } /* Literal.Number.Float */
.highlight .mh { color: #3677a9 } /* Literal.Number.Hex */
.highlight .mi { color: #3677a9 } /* Literal.Number.Integer */
.highlight .mo { color: #3677a9 } /* Literal.Number.Oct */
.highlight .sb { color: #ed9d13 } /* Literal.String.Backtick */
.highlight .sc { color: #ed9d13 } /* Literal.String.Char */
.highlight .sd { color: #ed9d13 } /* Literal.String.Doc */
.highlight .s2 { color: #ed9d13 } /* Literal.String.Double */
.highlight .se { color: #ed9d13 } /* Literal.String.Escape */
.highlight .sh { color: #ed9d13 } /* Literal.String.Heredoc */
.highlight .si { color: #ed9d13 } /* Literal.String.Interpol */
.highlight .sx { color: #ffa500 } /* Literal.String.Other */
.highlight .sr { color: #ed9d13 } /* Literal.String.Regex */
.highlight .s1 { color: #ed9d13 } /* Literal.String.Single */
.highlight .ss { color: #ed9d13 } /* Literal.String.Symbol */
.highlight .bp { color: #24909d } /* Name.Builtin.Pseudo */
.highlight .vc { color: #40ffff } /* Name.Variable.Class */
.highlight .vg { color: #40ffff } /* Name.Variable.Global */
.highlight .vi { color: #40ffff } /* Name.Variable.Instance */
.highlight .il { color: #3677a9 } /* Literal.Number.Integer.Long */



    

    :root {
        --ventionBlue:#1C344F;
        --accentBlue: #197CE0;
        --CTAGreen: #1AC876;
        --ventionGrey: #Eff2f7;
        --ventionDarkGrey: #BEC9CD;
        
        
        --t1: 19px;
        --t2: 14.9px;
        --t3: 11.8px;
        --t4: 9.2px;
        
        }
        
        
        a:hover {
            color:var(--ventionDarkGrey)
        }
        
        #div1 {
            background-color: var(--main-bg-color);
        }
        
        
        
        .indent1{
            margin-left: 25px;
        }
        
        .indent2{
            margin-left: 100px;
        }
        
        
        .funcWrapper {
            background: var(--ventionGrey);
            border-left: 2px solid var(--accentBlue);
            margin-top:5px;
            padding-left: 20px;
        }
        
        .funcClassName{
            font-size: var(--t3);
            font-style: italic;
            margin-left: -20px;
        }
        
        .funcName {
            font-size: var(--t2);
        }
        
        .funcParamHeading{
            font-size: var(--t2);
            font-style: italic;
            padding-right:10px;
            font-family: monospace;
        }
        
        .funcParam{
            color: var(--ventionBlue);
            font-size: var(--t2);
            font-family: monospace;
        }
        
        .funcParamType{
            color: var(--ventionBlue);
            font-size: var(--t3);
            
        }
        
        .funcText{
            margin-top: 10px;
            background: var(--ventionGrey);
            font-size: var(--t2);
        }
        
        .code-demo {
            width: 90%;
            font-size:0.8em;
            align-content: center;
        }
        
        
        .runCodeBtn {
            position: relative;
            bottom: -40px;
            left: 78%;
        }
        
        
        #sideNav .nav{
            border-left: 2px solid var(--ventionGrey);
        }
        
        .myTocHeader{
            font-size: var(--t2);
            color: var(--ventionDarkGrey);
            margin-left: 5px;
        }
        
        .myTocItem a{
            margin-top: 2px;
            padding-left: 10px;
            color: var(--ventionBlue);
            font-size: var(--t3);
            text-decoration: none;
        }
        
        .myTocItem a:hover{
            padding-left: 12px;
            color: var(--accentBlue);
            -moz-transition: padding-left.1s ease-in;
            -o-transition: padding-left  .1s ease-in;
            -webkit-transition: padding-left  .1s ease-in;
            transition: padding-left  .1s ease-in;
        }
        
        
        .sticky-side-nav {
            padding-top: 90px;
            position: fixed;
            top: 0;
            -moz-transition: padding-top.3s ease-in;
            -o-transition: padding-top  .3s ease-in;
            -webkit-transition: padding-top  .3s ease-in;
            transition: padding-top  .3s ease-in;
        }
        
        .api-button{
            font-size: var(--t3);
            display: inline-block;
            margin-right: 5px;
        }
        
        .card {
            margin: 0 auto; /* Added */
            float: none; /* Added */
            margin-bottom: 10px; /* Added */
        }
        
        .funcNote {
            width: 80%;
            margin-top: 10px;
            padding-top: 5px;
            padding-bottom: 10px;
            font-style: italic;
            font-size: var(--t3);
        
            border-top: 1px solid var(--ventionDarkGrey);
        }
        
        .requiredOptional {
        
            font-style: italic;
        }
        
        /* used to adjust the scroll height when menu nav is clicked */
        .anchor {
            display: block;
            position: relative;
            top: -250px;
            visibility: hidden;
        }
        
        code {
            color: var(--ventionBlue);
        }
        
        .card-text{
            word-wrap: break-word;
          }
        

</style>