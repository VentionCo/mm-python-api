{::accordion title='${func.name}' code=' \
% if func.parametersExist:
(${",".join(func.listParameters())}) \
% else:
( ) \
% endif
'}
**Comaptibility**: \
% if func.V1_compatible and func.V2_compatible:
MachineMotion v1 & MachineMotion v2
% elif func.V1_compatible:
MachineMotion V1 only
% elif func.V2_compatible:
MachineMotion V1 only
% endif

${'######'} **Description**
${func.desc}
% if func.parametersExist:
${'######'} **Parameters**
## loop through function parameters 
% for param in func.parameters:
**${param.paramName}** \
( \
% if param.optional:
Optional. Default = ${param.defaultValue} \
% else:
Required \
% endif   
) \
`${param.typeName}` - ${param.desc}
% endfor
% endif

${'######'} **Return Value**
%if func.returnValue is not None:
${func.returnValue}
%else:
None
%endif
% if func.noteExists:
**NOTE:** ${func.note}
% endif
% if func.V1_exampleCodeExists:
${'######'} MachineMotion V1 Example Code
```python
${func.V1_exampleCodeText}
```
% endif
% if func.V2_exampleCodeExists:
${'######'} MachineMotion V2 Example Code
```python
${func.V2_exampleCodeText}
```
% endif
{:/accordion}