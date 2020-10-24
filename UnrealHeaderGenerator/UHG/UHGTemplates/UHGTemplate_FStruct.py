
def GetTemplateInfo():
	className = 'F${name}Struct'
	templateName = 'FStruct'
	templateContent = '''
#pragma once

// unreal headers
#include "CoreMinimal.h"

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

// using ${namespace}::F${alias} = ${className};
''';

	return templateName, templateContent, className