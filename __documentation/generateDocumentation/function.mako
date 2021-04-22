<dl class="funcWrapper" >
    <dt id=${func.name}  style="cursor:pointer;" data-toggle="collapse" href= "#${func.name + 'showDescription'}" >
        <div class = "row">
            <div class = "col-md-8">
                <h3> 
                    <span class = "funcName"> <b>${func.name}</b> </span>
                    % if func.parametersExist:
                        (<span class="func funcParamHeading">
                                ${",".join(func.listParameters())}
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

        <button style="padding-left:0; text-align:left" type="button" class="btn btn-link btn-block" data-toggle="collapse" href= "#${func.name + 'collapseSource'}">
            <h4>Source Code <i class="fas fa-chevron-down"></i></h4>
        </button>

        <div class="collapse" data-parent ="#${func.name + 'collapseParent'}" id="${func.name + 'collapseSource'}">
                ${func.sourceCodeHtml}
        </div>


        % if func.V1_exampleCodeExists:
        <div>
            <button style="padding-left:0; text-align:left" type="button" class="btn btn-link btn-block" data-toggle="collapse" href= "#${func.name + 'v1_collapseExample'}"><h4>MachineMotion V1 Example Code</h4> <i class="fas fa-chevron-down"></i></button>
        </div>

        <div class= "collapse"  id="${func.name + 'v1_collapseExample'}">
            <button type="button" data-parent ="#${func.name + 'collapseParent'}"  class="runCodeBtn button button-success button-xs" onclick="copyTextToClipboard('${func.name + 'exampleCode'}', '${func.name}')">
            <i class="fas fa-copy"></i>  Copy Code
            </button>
            <div id = "${func.name + 'v1_exampleCode'}">
                ${func.V1_exampleCodeHtml}
            </div>
        </div>
        % endif

        % if func.V2_exampleCodeExists:
        <div>
            <button style="padding-left:0; text-align:left" type="button" class="btn btn-link btn-block" data-toggle="collapse" href= "#${func.name + 'v2_collapseExample'}"><h4>MachineMotion V2 Example Code</h4> <i class="fas fa-chevron-down"></i></button>
        </div>

        <div class= "collapse"  id="${func.name + 'v2_collapseExample'}">
            <button type="button" data-parent ="#${func.name + 'collapseParent'}"  class="runCodeBtn button button-success button-xs" onclick="copyTextToClipboard('${func.name + 'exampleCode'}', '${func.name}')">
            <i class="fas fa-copy"></i>  Copy Code
            </button>
            <div id = "${func.name + 'v2_exampleCode'}">
                ${func.V2_exampleCodeHtml}
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
