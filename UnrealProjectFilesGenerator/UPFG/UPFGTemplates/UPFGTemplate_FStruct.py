
def GetTemplateInfo():
	className = 'F${name}Struct'
	templateName = 'FStruct'
	templateContent = '''
#pragma once

// unreal headers
#include "CoreMinimal.h"

% if 'includes' in TemplateData.data:
// custom headers
% for include in TemplateData.data["includes"]:
#include "${Settings.GetIncludePath(include)}"
% endfor
% endif

// generated headers
#include "${className}.generated.h"

USTRUCT(${metadata["ustruct"] if 'ustruct' in metadata else ''})
struct ${Settings.GetAPI()} ${className} {
	GENERATED_CLASS()

% for member in members:
	UPROPERTY(${member["metadata"]})
	${member["declaration"]};

% endfor

% for func in functions:
	${func["declaration"]};
% endfor
};

// using ${namespace}::F${TemplateData.GetAlias()} = ${className};
''';

	return templateName, templateContent, className