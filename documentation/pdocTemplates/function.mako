<dl class="funcWrapper" >
    <dt id=${func.name}  style="cursor:pointer;" data-toggle="collapse" href= "#${func.name + 'showDescription'}" >
        <div class = "row">
            <div class = "col-md-8">
                <h3> 
                    <span class = "funcName"> <b>${func.name}</b> </span>
                    % if func.parametersExist:
                        (<span class="func funcParamHeading">
                                ${func.listParameters()}
                            </span>)
                    % else:
                    ( )
                    % endif
                </h3>
            </div>
        </div>
    </dt>
    <div class="collapse" data-parent ="#${func.name + 'showDescription'}" id="${func.name + 'showDescription'}">
        <dd>
            <div class="funcText"> <b>Description </b></div>
            <div class="funcText indent1">
                ${func.desc}
            </div>
        </dd>


        % if func.parametersExist:
        <h4> Parameters </h4>
            % for param in func.parameters:
                <div class="indent1">
                    <span class = "funcParam"><b>${param.paramName}</b></span>
                    <span style="requiredOptional" class ="funcParamType">
                        (
                        % if param.optional:
                        Optional. Default = ${param.defaultValue} 
                        % else:
                        Required
                        % endif   
                        )
                    </span>
                    <span class = "funcParamType"><code>${param.typeName}</code></span>
                    -
                    <span class = "funcText">          
                        ${param.desc}
                    </span>
                </div>
            % endfor
        % endif

        <h4> Return Value </h4>
        <div class = "indent1 funcText">
            %if func.returnValue is not None:
            ${func.returnValue}
            %else:
            None
            %endif
        </div>

        <div>
            <button style="padding-left:0; text-align:left" type="button" class="btn btn-link btn-block" data-toggle="collapse" href= "#${func.name + 'collapseSource'}"><h4>Source Code <i class="fas fa-chevron-down"></i></h4></button>
        </div>
        <div class="card card-body code-demo"  >
            <div class="collapse" data-parent ="#${func.name + 'collapseParent'}" id="${func.name + 'collapseSource'}">
                <div class="card card-body  code-demo">
                    ${func.sourceCodeHtml}
                </div>
            </div>
        </div>


        % if func.exampleCodeExists:
        <div>
            <button style="padding-left:0; text-align:left" type="button" class="btn btn-link btn-block" data-toggle="collapse" href= "#${func.name + 'collapseExample'}"><h4>Example Code</45> <i class="fas fa-chevron-down"></i></button>
        </div>
        <div class= "collapse"  id="${func.name + 'collapseExample'}">

        <div class="card card-body code-demo" >
        <button type="button" data-parent ="#${func.name + 'collapseParent'}"  class="runCodeBtn button button-success button-xs" onclick="copyTextToClipboard('${func.name + 'exampleCode'}', '${func.name}')"><i class="fas fa-copy"></i>  Copy Code</button>
                <div class="card card-body code-demo" id = "${func.name + 'exampleCode'}">
                    ${func.exampleCodeHtml}
                </div>
            </div>
        </div>
        % endif



 
        % if func.noteExists:
        <dd >
            <div class="funcNote">
                <div class="d-inline"><b>NOTE:</b></div>
                <div class="d-inline">${func.note}</div>
            </div>

        </dd>
        %endif
        <div style="height:10px">
        </div>
    </div>
</dl>
